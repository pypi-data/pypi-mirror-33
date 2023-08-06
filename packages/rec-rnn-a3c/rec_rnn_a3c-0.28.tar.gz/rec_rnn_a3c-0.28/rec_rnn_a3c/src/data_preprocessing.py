from __future__ import division

import os
import sys

import operator

import numpy
from tensorflow.python.framework.errors_impl import DataLossError

sys.path.append(os.path.join(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0], '..'))

import csv
import json
import tempfile
import threading
import multiprocessing


import boto3 as boto3
import pandas as pd
import tensorflow as tf
import botocore as botocore

from multiprocessing.pool import ThreadPool

from rec_rnn_a3c.src.util import replace_multiple, get_all_s3_keys, s3_download

S3 = boto3.client('s3', aws_access_key_id=os.environ.get('S3_KEY'), aws_secret_access_key=os.environ.get('S3_SECRET'))
BUCKET = 'rec-rnn-mpd'
WORKING_DIR = os.path.join(tempfile.gettempdir(), BUCKET)
DUMMY_FILENAMES = ["/Users/Tim/Documents/mpd.v1/data/mpd.slice.0-999.json",
                   "/Users/Tim/Documents/mpd.v1/data/mpd.slice.1000-1999.json"]

MAPPER = 'map'
DATA = 'data'
PREPROC_DATA = 'new_preproc_data'

URI_TO_FREQUENCY = 'uri-to-frequency.csv'
URI_TO_ID = 'uri-to-id.csv'
ID_TO_URI = 'id-to-uri.csv'
PLAYLIST_DATAFRAME = 'playlist-dataframe.csv'
MARKET_CHECKER = 'uri_with_markets.csv'

class DataPreprocessor(object):
    def __init__(self, working_dir, files, num_examples, train_fraction=0.9):
        self.working_dir = working_dir
        self.files = files
        self.num_examples = num_examples
        self.train_fraction = train_fraction

        print("Set working dir to: %s" % working_dir)

        self.uri_to_frequency = None
        self.uri_to_id = None

    def _calculate_track_frequencies(self, file):
        file_path = os.path.join(self.working_dir, file)
        if s3_download(S3, file, BUCKET, working_dir):
            print("Downloaded %s from S3 Bucket %s" % (file, BUCKET))

        with open(file_path) as json_raw:
            current_thread = threading.currentThread()

            print("Thread %s: Start processing file %s" % (current_thread, file))

            json_data = json.load(json_raw)
            data_frame = pd.DataFrame.from_dict(json_data['playlists'])

            all_playlist_tracks = {}
            for index, row in data_frame[['pid', 'tracks']].iterrows():
                pid = row['pid']
                playlist_tracks = row['tracks']
                df_playlist_tracks = pd.DataFrame(playlist_tracks)
                all_playlist_tracks[pid] = df_playlist_tracks

            uri_to_frequency = {}
            for pid, df_tracks in all_playlist_tracks.iteritems():
                for _, track_uri in df_tracks['track_uri'].iteritems():
                    if track_uri in uri_to_frequency:
                        uri_to_frequency[track_uri] += 1
                    else:
                        uri_to_frequency[track_uri] = 1
            print("Thread %s: Finished processing file %s" % (current_thread, file))
            return uri_to_frequency

    def calculate_uri_to_freq(self, save=False):
        working_dir = os.path.join(self.working_dir, MAPPER)

        print("Now calculating... %s" % URI_TO_FREQUENCY)
        # Prepare Working Dir
        if not os.path.exists(working_dir):
            print("Created new dir %s" % working_dir)
            os.makedirs(working_dir)

        # Thread Pool for Parallelization
        num_threads = multiprocessing.cpu_count()
        pool = ThreadPool(processes=num_threads)

        results = pool.map(self._calculate_track_frequencies, self.files)
        pool.close()
        pool.join()

        # Combine parallelized results
        uri_to_frequency = {}
        for mapper in results:
            for track_uri, frequency in mapper.iteritems():
                if track_uri in uri_to_frequency:
                    uri_to_frequency[track_uri] += frequency
                else:
                    uri_to_frequency[track_uri] = frequency

        self.uri_to_frequency = uri_to_frequency

        uri_to_freq_path = os.path.join(working_dir, URI_TO_ID)
        with open(uri_to_freq_path, 'wb') as f:
            writer = csv.writer(f)
            for key, value in uri_to_frequency.items():
                writer.writerow([key, value])
        print("Saved %s successfully" % URI_TO_FREQUENCY)

    def calculate_uri_to_id(self):
        print("Now calculating... %s" % URI_TO_ID)

        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('S3_KEY'),
                          aws_secret_access_key=os.environ.get('S3_SECRET'))

        item_dim_indicator = 'map/uri-to-frequency.csv'
        s3_download(s3, item_dim_indicator, 'rec-rnn-mpd', self.working_dir)
        with open(os.path.join(self.working_dir, item_dim_indicator), 'rb') as f:
            self.uri_to_frequency = dict(csv.reader(f))

        # Sort subject to frequency
        sorted_uris = sorted(self.uri_to_frequency, key=self.uri_to_frequency.get)[::-1]


        uri_to_id = {}
        for idx, uri in enumerate(sorted_uris):
            uri_to_id[uri] = idx

        # Save to disk
        uri_to_id_path = os.path.join(working_dir, URI_TO_ID)
        with open(uri_to_id_path, 'wb') as f:
            writer = csv.writer(f)
            for key, value in uri_to_id.items():
                writer.writerow([key, value])
        print("Saved %s successfully" % URI_TO_ID)

        self.uri_to_id = uri_to_id

    def _make_example(self, sequence, labels):
        ex = tf.train.SequenceExample()
        fl_tokens = ex.feature_lists.feature_list["train/sequence"]
        fl_labels = ex.feature_lists.feature_list["train/labels"]
        for token, label in zip(sequence, labels):
            fl_tokens.feature.add().int64_list.value.append(token)
            fl_labels.feature.add().int64_list.value.append(label)
        return ex

    def _convert_to_tfrecords(self, file):
        current_thread = threading.currentThread()
        print("Thread %s: Start processing file %s" % (current_thread, file))

        file_path = os.path.join(self.working_dir, file)

        type = 'train' if int(file.split('.')[-2].split('-')[-1]) / self.num_examples < self.train_fraction else 'eval'

        conv_file_path = replace_multiple(file_path, {DATA: PREPROC_DATA, 'json': type + '.tfrecords'})

        if os.path.isfile(conv_file_path):
            print("Thread %s: Converted file %s already exists." % (current_thread, file))
        else:
            if not os.path.isfile(file_path):
                try:
                    S3.download_file(BUCKET, file, file_path)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "404":
                        print("Thread %s: File %s does not exist in S3." % (current_thread, file))
                    else:
                        raise

            with open(file_path) as json_raw:
                json_data = json.load(json_raw)
                data_frame = pd.DataFrame.from_dict(json_data['playlists'])

                sequences = []
                label_sequences = []
                for index, row in data_frame[['pid', 'tracks']].iterrows():
                    playlist_tracks = row['tracks']

                    # For including all instances
                    #seq = [self.uri_to_id[t['track_uri']] for t in playlist_tracks


                    #For filtered uri_to_id
                    seq = []
                    for t in playlist_tracks:
                        try:
                            cand = self.uri_to_id[t['track_uri']]
                            if cand > len(self.uri_to_id):
                                print("Found %d - skipping...")
                            else:
                                seq.append(cand)
                        except KeyError:
                            #print("Key %s not included - not frequent enough" % t['track_uri'])
                            pass

                    sequences.append(seq[:-1])
                    label_sequences.append(seq[1:])

                with open(conv_file_path, 'wb') as fp:
                    writer = tf.python_io.TFRecordWriter(fp.name)
                    for sequence, label_sequence in zip(sequences, label_sequences):
                        ex = self._make_example(map(int, sequence), map(int, label_sequence))
                        writer.write(ex.SerializeToString())
                    writer.close()
                    print('Thread %s: Saved file %s ...' % (current_thread, conv_file_path))

    def calculate_dataset(self):
        data_dir = os.path.join(self.working_dir, DATA)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('S3_KEY'),
                          aws_secret_access_key=os.environ.get('S3_SECRET'))

        uri_to_freq_path = 'final_dataset/uri-to-frequency.csv'
        s3_download(s3, uri_to_freq_path, 'rec-rnn-mpd', working_dir)
        with open(os.path.join(working_dir, uri_to_freq_path), 'rb') as f:
            uri_to_frequency = dict(csv.reader(f))

        counter = 0
        uri_to_id = {}
        for key, value in uri_to_frequency.items():
            freq = int(uri_to_frequency[key])
            if freq > 2000:
                uri_to_id[key] = counter
                counter += 1


        self.uri_to_id = uri_to_id
        print(len(self.uri_to_id))

        uri_to_id_path = os.path.join(working_dir, URI_TO_ID)
        with open(uri_to_id_path, 'wb') as f:
            writer = csv.writer(f)
            for key, value in self.uri_to_id.items():
                writer.writerow([key, value])
        print("Saved %s successfully" % URI_TO_ID)

        preproc_data_dir = os.path.join(self.working_dir, PREPROC_DATA)
        if not os.path.exists(preproc_data_dir):
            os.makedirs(preproc_data_dir)

        for _ in self.files:
            num_threads = multiprocessing.cpu_count()
            pool = ThreadPool(processes=num_threads)
            pool.map(self._convert_to_tfrecords, self.files)
            pool.close()

    def combine_sliced_files(self):
        data_dir = os.path.join(self.working_dir, PREPROC_DATA)
        if not os.path.exists(data_dir):
            self.calculate_dataset()

        save_dir = os.path.join(self.working_dir, '50k_dataset')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        #files = filter(lambda x: 'tfrecords' in x, get_all_s3_keys(S3, BUCKET))
        #files = filter(lambda x: 'new_preproc_data' in x, files)
        #train_files = filter(lambda x: 'train' in x, files)
        #train_files = filter(lambda x: 'eval' in x, files)

        #for file in train_files:
            #S3.download_file(BUCKET, file, os.path.join(self.working_dir, file))

        train_files = os.listdir(data_dir)
        train_files = filter(lambda x: 'eval' in x, train_files)

        def _parse_function(example_proto):
            features = {
                "train/sequence": tf.FixedLenSequenceFeature([], dtype=tf.int64),
                "train/labels": tf.FixedLenSequenceFeature([], dtype=tf.int64)
            }

            _, sequence_parsed = tf.parse_single_sequence_example(
                serialized=example_proto,
                sequence_features=features
            )

            return sequence_parsed['train/sequence'], sequence_parsed['train/labels']

        files_placeholder = tf.placeholder(tf.string, shape=[None])

        data_set = tf.data.TFRecordDataset(files_placeholder)
        data_set = data_set.map(_parse_function)
        iterator = data_set.make_initializable_iterator()
        next_seq = iterator.get_next()

        sequences = []
        label_sequences = []
        with tf.Session() as sess:
            sess.run(
                iterator.initializer,
                feed_dict={files_placeholder: [os.path.join(data_dir, t) for t in train_files]})

            counter = 0
            print("Collecting sequences...")
            while True:
                try:
                    seq, label_seq = sess.run(next_seq)
                    sequences.append(seq)
                    label_sequences.append(label_seq)
                    counter += 1

                    if counter % 1000 == 0:
                        print("Processed %d examples..." % counter)
                except tf.errors.OutOfRangeError:
                    break
                except DataLossError as e:
                    print e

        counter = 0
        print("Writing to file...")
        with open(os.path.join(save_dir, 'spotify.eval.tfrecords'), 'wb') as fp:
            writer = tf.python_io.TFRecordWriter(fp.name)
            for sequence, label_sequence in zip(sequences, label_sequences):
                ex = self._make_example(map(int, sequence), map(int, label_sequence))
                writer.write(ex.SerializeToString())

                counter += 1
                if counter % 1000 == 0:
                    print("Written %d examples..." % counter)
            writer.close()
            print('Saved file %s ...' % save_dir)

    def _get_valid_uri(self, sequence, valid_uris):
        while len(sequence) > 0:
            next_candidate = sequence.pop()
            if next_candidate in valid_uris:
                return next_candidate

        return None

    # TODO: Convert to invalid uris
    def _make_valid_example(self, sequence, labels, valid_uris):
        ex = tf.train.SequenceExample()
        fl_tokens = ex.feature_lists.feature_list["train/sequence"]
        fl_labels = ex.feature_lists.feature_list["train/labels"]

        token = self._get_valid_uri(sequence, valid_uris)
        label = self._get_valid_uri(labels, valid_uris)
        while token is not None and label is not None:
            fl_tokens.feature.add().int64_list.value.append(token)
            fl_labels.feature.add().int64_list.value.append(label)

            token = self._get_valid_uri(sequence, valid_uris)
            label = self._get_valid_uri(labels, valid_uris)

        for token, label in zip(sequence, labels):

            fl_tokens.feature.add().int64_list.value.append(token)
            fl_labels.feature.add().int64_list.value.append(label)
        return ex



if __name__ == "__main__":
    working_dir = os.path.join(tempfile.gettempdir(), BUCKET)
    files = filter(lambda x: 'json' in x, get_all_s3_keys(S3, BUCKET))
    num_examples = int(files[-1].split('.')[-2].split('-')[-1])
    data_preprocessor = DataPreprocessor(
        working_dir=working_dir,
        files=files,
        num_examples=num_examples
    )

    #data_preprocessor.calculate_uri_to_freq()
    #data_preprocessor.calculate_uri_to_id()
    data_preprocessor.calculate_dataset()
    #data_preprocessor.combine_sliced_files()




