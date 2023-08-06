from copy import deepcopy

import numpy as np
import tensorflow as tf
import time
from rec_rnn_a3c.src.supervised_rnn import SupervisedRNN

tf.logging.set_verbosity(tf.logging.INFO)


class SupervisedRNNModel(object):
    def __init__(self, optimizer, params, scope='supervised_rnn'):
        self.optimizer = optimizer

        self.params = params

        self.unfold_dim = params['unfold_dim']
        self.item_dim = params['item_dim']

        #self.reward_network = SupervisedBloomRNN(optimizer=optimizer, params=params, scope=scope)
        self.reward_network = SupervisedRNN(optimizer=optimizer, params=params, scope=scope)

        self.files = tf.placeholder(tf.string, shape=[None], name='files')

        self.merged_summary = tf.summary.merge_all()

    def predict(self, seq, sess, num_predictions=1, remove_doubles=True):
        seq_len = len(seq)

        diff = self.unfold_dim - seq_len
        padded_seq = deepcopy(seq)
        if diff < 0:
            padded_seq = padded_seq[-diff:]
        elif diff > 0:
            padded_seq += [0 for _ in range(self.unfold_dim - seq_len)]

        padded_seq = map(int, padded_seq)
        padded_seq = np.expand_dims(padded_seq, axis=0)

        feed_dict = {
            self.reward_network.input: padded_seq,
            self.reward_network.keep_prob: 1.0,
            self.reward_network.target_index: seq_len - 1
        }

        fetches = [self.reward_network.partial_prob_dist]

        probs = sess.run(feed_dict=feed_dict, fetches=fetches)
        probs = np.array(probs)
        probs = np.reshape(probs, newshape=[-1])

        probs[seq] = 0

        predictions = probs.argsort()[-num_predictions:][::-1]
        return np.reshape(predictions, [-1])

    def predict_sequential(self, seq, sess, num_predictions=1):
        seq_len = len(seq)

        diff = self.unfold_dim - seq_len
        if diff < 0:
            seq = seq[-diff:]
        elif diff > 0:
            seq += [0 for _ in range(self.unfold_dim - seq_len)]

        seq = map(int, seq)
        seq = np.expand_dims(seq, axis=0)

        feed_dict = {
            self.reward_network.input: seq,
            self.reward_network.keep_prob: 1.0,
            self.reward_network.target_index: seq_len - 1
        }

        fetches = [self.reward_network.partial_prob_dist]
        predictions = []

        for i in range(0, num_predictions):
            probs = sess.run(feed_dict=feed_dict, fetches=fetches)
            probs = np.reshape(probs, [-1, self.item_dim])

            #sorted_probs = np.sort(probs, axis=1)[0][::-1]

            prediction_ = np.argmax(probs, axis=1)
            print(prediction_)
            seq[0, seq_len + i] = prediction_[0]
            seq_len += 1

            feed_dict = {
                self.reward_network.input: seq,
                self.reward_network.target_index: seq_len - 1,
                self.reward_network.keep_prob: 1.0,
            }

            predictions.append(prediction_)

        return np.reshape(predictions, [-1])

    def eval(self, sess, iterator):
        next_element = iterator.get_next()

        total_loss = 0.0
        total_recall = 0.0
        total_steps = 0
        while True:
            try:
                step_loss = 0.0
                step_recall = 0.0
                sequence, label_sequence = sess.run(next_element)

                # TODO: Improve
                if np.shape(sequence)[0] != self.params['batch_dim']:
                    break

                num_sequence_splits = np.max([1, np.shape(sequence)[1] // self.unfold_dim])

                for split in range(num_sequence_splits):
                    seq_split = sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]
                    label_seq_split = label_sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]

                    feed_dict = {
                        self.reward_network.input: seq_split,
                        self.reward_network.labels: label_seq_split,
                        self.reward_network.keep_prob: 1.0,
                    }

                    fetches = [
                        self.reward_network.loss,
                        #self.reward_network.recall
                    ]

                    loss = sess.run(
                        feed_dict=feed_dict,
                        fetches=fetches
                    )

                    step_loss += loss[0]
                    step_recall += 0
                    #step_recall += recall[0][1]

                    total_steps += 1

                total_loss += step_loss / num_sequence_splits
                total_recall += step_recall / num_sequence_splits
            except (tf.errors.OutOfRangeError, tf.errors.InvalidArgumentError):
                break

        tf.logging.info("Evaluation -- Loss: %s -- Recall: %s"
                        % (total_loss / total_steps, (total_recall / total_steps)))

    def fit(self, sess, iterator, epoch, num_epochs, iteration, num_iterations):
        #train_writer = tf.summary.FileWriter(save_path + '/train', sess.graph)

        next_element = iterator.get_next()

        total_loss = 0.0
        time_deltas = 0.0
        for i in range(iteration, num_iterations):
            start = time.time()
            try:
                step_loss = 0.0
                # TODO: Possible without feeding? (Improves performance)
                sequence, label_sequence = sess.run(next_element)

                # TODO: Reset states?
                #self.rnn_state_c, self.rnn_state_h = self.reward_network.rnn_zero_state

                num_sequence_splits = np.max([1, np.shape(sequence)[1] // self.unfold_dim])

                for split in range(num_sequence_splits):
                    seq_split = sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]
                    label_seq_split = label_sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]

                    feed_dict = {
                        self.reward_network.input: seq_split,
                        self.reward_network.labels: label_seq_split
                    }

                    fetches = [
                        self.reward_network.loss,
                        self.reward_network.train_op,
                    ]

                    loss, _ = sess.run(
                        feed_dict=feed_dict,
                        fetches=fetches
                    )
                    step_loss += loss

                total_loss += step_loss / num_sequence_splits
            except tf.errors.OutOfRangeError:
                break
            end = time.time()

            time_delta = end - start
            time_deltas += time_delta

            if i % 50 == 0:
                tf.logging.info(
                    "Episode [%d/%d]@[%d/%d] -- Avg. Error: %s -- Total Time: %3f s"
                    % (epoch, num_epochs, i, num_iterations, total_loss / (i+1), time_deltas))

        tf.logging.info(
            "Episode [%d/%d]@complete -- Error: %s -- Average Time: %3f secs"
            % (epoch, num_epochs, total_loss / num_iterations, time_deltas))

            #summary, _ = sess.run([self.merged_summary, self.reward_network.loss], feed_dict=feed_dict)
            #train_writer.add_summary(summary, iteration * num_steps + step)