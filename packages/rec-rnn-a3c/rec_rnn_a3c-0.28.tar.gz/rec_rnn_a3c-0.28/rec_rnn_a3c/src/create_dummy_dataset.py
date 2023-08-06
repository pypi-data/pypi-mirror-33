import os
import tempfile

import tensorflow as tf

working_dir = os.path.join(tempfile.gettempdir(), 'rec-rnn-mpd')
save_dir = os.path.join(working_dir, '2seq_dummy_dataset')
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

sequences = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
]

label_sequences = [
    [2, 3, 4, 5, 6, 7, 8, 9, 10, 1],
    [1, 10, 9, 8, 7, 6, 5, 4, 3, 2]
]


def _make_example(sequence, labels):
    ex = tf.train.SequenceExample()
    fl_tokens = ex.feature_lists.feature_list["train/sequence"]
    fl_labels = ex.feature_lists.feature_list["train/labels"]
    for token, label in zip(sequence, labels):
        fl_tokens.feature.add().int64_list.value.append(token)
        fl_labels.feature.add().int64_list.value.append(label)
    return ex

with open(os.path.join(save_dir, 'spotify.eval.tfrecords'), 'wb') as fp:
    writer = tf.python_io.TFRecordWriter(fp.name)
    for sequence, label_sequence in zip(sequences, label_sequences):
        ex = _make_example(map(int, sequence), map(int, label_sequence))
        writer.write(ex.SerializeToString())

    print("Dataset saved to: %s" % save_dir)