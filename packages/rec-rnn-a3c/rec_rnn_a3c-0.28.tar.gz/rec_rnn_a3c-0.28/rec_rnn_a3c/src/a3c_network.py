import numpy as np
import tensorflow as tf
from tensorflow.contrib import slim
from tensorflow.python.ops.rnn import raw_rnn

from rec_rnn_a3c.src.supervised_rnn import length
from rec_rnn_a3c.src.util import normalized_columns_initializer

class MetaA3CNetwork0(object):
    def __init__(self, scope, optimizer, params):
        self.scope = scope
        with tf.variable_scope(self.scope):
            self.optimizer = optimizer

            self.item_dim = params['item_dim']
            self.output_dim = params['output_dim']
            self.hidden_dim = params['hidden_dim']
            self.batch_dim = params['batch_dim']
            self.unfold_dim = params['unfold_dim']

            self.sample_size = params['sample_size']

            self.supervised_target = tf.placeholder(tf.int64, [self.batch_dim, None], name='target')

            self.state = tf.placeholder(tf.int32, shape=[None, None], name='input')

            with tf.device("/cpu:0"):
                embedding_table = tf.get_variable(name="embedding_table", shape=[self.item_dim, self.hidden_dim])
                embedded_state = tf.nn.embedding_lookup(params=embedding_table, ids=self.state)

            self.keep_prob = tf.placeholder_with_default(0.5, shape=[], name='keep_prob')
            rnn_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_dim, state_is_tuple=True)
            rnn_cell = tf.nn.rnn_cell.DropoutWrapper(rnn_cell, output_keep_prob=self.keep_prob)

            self.length = length(self.state)

            self.policy_weights = tf.get_variable("policy_weights", [self.item_dim, self.hidden_dim], dtype=tf.float32)
            self.policy_bias = tf.get_variable("policy_bias", [self.item_dim], dtype=tf.float32)

            rnn_output = []
            rnn_state = rnn_cell.zero_state(self.batch_dim, dtype=tf.float32)
            with tf.variable_scope("RNN"):
                for time_step in range(self.unfold_dim):
                    if time_step == 0:
                        reward = tf.zeros([self.batch_dim, 1])
                        cell_output = tf.zeros([self.batch_dim, self.hidden_dim])
                    else:
                        tf.get_variable_scope().reuse_variables()

                        loss = tf.nn.sampled_softmax_loss(
                            weights=self.policy_weights,
                            biases=self.policy_bias,
                            labels=tf.reshape(self.supervised_target[:, time_step-1], shape=[self.batch_dim, 1]),
                            inputs=cell_output,
                            num_sampled=self.sample_size,
                            num_classes=self.item_dim)
                        reward = tf.reshape(1.0 - loss, shape=[self.batch_dim, 1])

                    rnn_inputs = tf.concat([embedded_state[:, time_step, :], reward, cell_output], axis=1)

                    (cell_output, rnn_state) = rnn_cell(rnn_inputs, rnn_state)
                    rnn_output.append(cell_output)
                rnn_output = tf.reshape(tf.concat(rnn_output, 1), [self.batch_dim, -1, self.hidden_dim])

            output_shape = tf.shape(rnn_output)

            self.value_weights = tf.get_variable("value_weights", [self.hidden_dim, 1], dtype=tf.float32)

            # Probability estimations for complete sequence
            self.policy_logit_output = tf.matmul(tf.reshape(rnn_output, [-1, self.hidden_dim]), self.policy_weights, transpose_b=True)
            self.policy_logit_output = tf.nn.bias_add(self.policy_logit_output, self.policy_bias)
            self.policy_logit_output = tf.reshape(self.policy_logit_output, [output_shape[0], output_shape[1], self.item_dim])
            self.policy_prob_output = tf.nn.softmax(self.policy_logit_output)

            self.value_output = tf.matmul(tf.reshape(rnn_output, [-1, self.hidden_dim]), self.value_weights)
            self.value_output = tf.reshape(self.value_output, [output_shape[0], output_shape[1]])

            # Probability estimations for final output only
            final_rnn_output = rnn_output[:, -1, :]

            self.policy_logit_output_at_T = tf.matmul(final_rnn_output, self.policy_weights, transpose_b=True)
            self.policy_logit_output_at_T = tf.nn.bias_add(self.policy_logit_output_at_T, self.policy_bias)
            self.policy_prob_output_at_T = tf.nn.softmax(self.policy_logit_output_at_T)

            self.action_at_T = tf.argmax(self.policy_logit_output_at_T, axis=1)
            self.overlap_at_T = tf.equal(self.action_at_T, self.supervised_target[:, -1])

            self.value_output_at_T = tf.matmul(final_rnn_output, self.value_weights)

            # Critic #
            self.actions = tf.placeholder(shape=[None, None], dtype=tf.int32, name='actions')
            actions = tf.one_hot(self.actions, self.output_dim, dtype=tf.float32)
            self.value_target = tf.placeholder(shape=[None, None], dtype=tf.float32, name='value_target')
            self.advantages = tf.placeholder(shape=[None, None], dtype=tf.float32, name='advantages')

            self.policy_estimate = tf.reduce_sum(tf.multiply(self.policy_logit_output, actions), axis=2)

            # Loss functions.
            value_output = tf.reshape(self.value_output, tf.shape(self.value_target))
            self.value_loss = 0.5 * tf.reduce_sum(tf.square(self.value_target - value_output))
            self.policy_loss = - tf.reduce_sum(self.policy_estimate * self.advantages)
            self.entropy = - tf.reduce_sum(self.policy_logit_output * self.policy_prob_output)

            self.supervised_loss = tf.nn.sampled_softmax_loss(
                weights=self.policy_weights,
                biases=self.policy_bias,
                labels=tf.reshape(self.supervised_target, [-1, 1]),
                inputs=tf.reshape(rnn_output, [-1, self.hidden_dim]),
                num_sampled=self.sample_size,
                num_classes=self.item_dim)
            self.supervised_loss = tf.reshape(self.supervised_loss, [output_shape[0], output_shape[1]])
            self.supervised_loss = tf.reduce_mean(self.supervised_loss, axis=0)
            self.supervised_loss = tf.reduce_sum(self.supervised_loss)

            self.loss = self.supervised_loss
            #self.loss = 0.5 * self.value_loss + 1.0 * self.policy_loss - 0.1 * self.entropy
            #self.loss = 1.0 * self.sv_loss + 0.25 * self.value_loss + 0.5 * self.policy_loss - 0.05 * self.entropy

            self.advantages_sum = tf.reduce_sum(self.advantages)

            trainable_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, self.scope)
            gradients = tf.gradients(self.loss, trainable_vars)
            clipped_gradients, _ = tf.clip_by_global_norm(gradients, 5.0)

            self.train_op = optimizer.apply_gradients(zip(clipped_gradients, trainable_vars))




class MetaA3CNetwork(object):
    def __init__(self, scope, optimizer, params):
        self.scope = scope
        with tf.variable_scope(self.scope):
            self.optimizer = optimizer

            self.item_dim = params['item_dim']
            self.output_dim = params['output_dim']
            self.hidden_dim = params['hidden_dim']
            self.batch_dim = params['batch_dim']
            self.unfold_dim = params['unfold_dim']

            self.sample_size = params['sample_size']

            self.supervised_target = tf.placeholder(tf.int64, [self.batch_dim, None], name='target')

            self.state = tf.placeholder(tf.int32, shape=[None, None], name='input')

            with tf.device("/cpu:0"):
                embedding_table = tf.get_variable(name="embedding_table", shape=[self.item_dim, self.hidden_dim])
                embedded_state = tf.nn.embedding_lookup(params=embedding_table, ids=self.state)

            self.keep_prob = tf.placeholder_with_default(0.5, shape=[], name='keep_prob')
            rnn_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_dim, state_is_tuple=True)
            rnn_cell = tf.nn.rnn_cell.DropoutWrapper(rnn_cell, output_keep_prob=self.keep_prob)

            self.sequence_length = length(self.state)

            self.policy_weights = tf.get_variable("policy_weights", [self.item_dim, self.hidden_dim], dtype=tf.float32)
            self.policy_bias = tf.get_variable("policy_bias", [self.item_dim], dtype=tf.float32)

            #sequence_length = tf.placeholder(shape=(batch_size,), dtype=tf.int32)
            #inputs_ta = tf.TensorArray(dtype=tf.float32, size=self.unfold_dim)
            #inputs_ta = inputs_ta.unstack(tf.transpose(embedded_state, [1,0,2]))
            #inputs_ta = inputs_ta.unstack(embedded_state)

            def loop_fn(time, cell_output, cell_state, loop_state):
                emit_output = cell_output  # == None for time == 0
                if cell_output is None:  # time == 0
                    next_cell_state = rnn_cell.zero_state(self.batch_dim, tf.float32)
                    cell_output = tf.zeros([self.batch_dim, self.hidden_dim])
                else:
                    next_cell_state = cell_state

                elements_finished = (time >= self.sequence_length)
                finished = tf.reduce_all(elements_finished)

                def unfinished_input():
                    if cell_output is None:
                        reward = tf.zeros([self.batch_dim, 1], dtype=tf.float32)
                        action_oh = tf.zeros([self.batch_dim, self.hidden_dim], dtype=tf.float32)
                    else:
                        loss = tf.nn.sampled_softmax_loss(
                            weights=self.policy_weights,
                            biases=self.policy_bias,
                            # TODO: Read input
                            labels=tf.reshape(self.supervised_target[:, time - 1], shape=[self.batch_dim, 1]),
                            inputs=cell_output,
                            num_sampled=self.sample_size,
                            num_classes=self.item_dim)
                        reward = tf.reshape(1.0 - loss, shape=[self.batch_dim, 1])

                        action_oh = cell_output

                    return tf.concat([embedded_state[:, time, :], action_oh, reward], axis=1)

                next_input = tf.cond(
                    finished,
                    lambda: tf.zeros([self.batch_dim, self.hidden_dim + self.hidden_dim + 1], dtype=tf.float32),
                    unfinished_input)
                next_loop_state = None
                return (elements_finished, next_input, next_cell_state,
                        emit_output, next_loop_state)

            outputs_ta, final_state, _ = raw_rnn(rnn_cell, loop_fn)
            rnn_output = outputs_ta.stack()

            rnn_output = tf.transpose(rnn_output, [1,0,2])
            output_shape = tf.shape(rnn_output)

            self.value_weights = tf.get_variable("value_weights", [self.hidden_dim, 1], dtype=tf.float32)

            # Probability estimations for complete sequence
            self.policy_logit_output = tf.matmul(tf.reshape(rnn_output, [-1, self.hidden_dim]), self.policy_weights, transpose_b=True)
            self.policy_logit_output = tf.nn.bias_add(self.policy_logit_output, self.policy_bias)
            self.policy_logit_output = tf.reshape(self.policy_logit_output, [output_shape[0], output_shape[1], self.item_dim])
            self.policy_prob_output = tf.nn.softmax(self.policy_logit_output)

            self.value_output = tf.matmul(tf.reshape(rnn_output, [-1, self.hidden_dim]), self.value_weights)
            self.value_output = tf.reshape(self.value_output, [output_shape[0], output_shape[1]])

            # Probability estimations for final output only
            final_rnn_output = rnn_output[:, -1, :]

            self.policy_logit_output_at_T = tf.matmul(final_rnn_output, self.policy_weights, transpose_b=True)
            self.policy_logit_output_at_T = tf.nn.bias_add(self.policy_logit_output_at_T, self.policy_bias)
            self.policy_prob_output_at_T = tf.nn.softmax(self.policy_logit_output_at_T)

            self.action_at_T = tf.argmax(self.policy_logit_output_at_T, axis=1)
            self.overlap_at_T = tf.equal(self.action_at_T, self.supervised_target[:, -1])

            self.value_output_at_T = tf.matmul(final_rnn_output, self.value_weights)

            # Critic #
            self.actions = tf.placeholder(shape=[None, None], dtype=tf.int32, name='actions')
            actions = tf.one_hot(self.actions, self.output_dim, dtype=tf.float32)
            self.value_target = tf.placeholder(shape=[None, None], dtype=tf.float32, name='value_target')
            self.advantages = tf.placeholder(shape=[None, None], dtype=tf.float32, name='advantages')

            self.policy_estimate = tf.reduce_sum(tf.multiply(self.policy_logit_output, actions), axis=2)

            # Loss functions.
            value_output = tf.reshape(self.value_output, tf.shape(self.value_target))
            self.value_loss = 0.5 * tf.reduce_sum(tf.square(self.value_target - value_output))
            self.policy_loss = - tf.reduce_sum(self.policy_estimate * self.advantages)
            self.entropy = - tf.reduce_sum(self.policy_logit_output * self.policy_prob_output)

            self.supervised_loss = tf.nn.sampled_softmax_loss(
                weights=self.policy_weights,
                biases=self.policy_bias,
                labels=tf.reshape(self.supervised_target, [-1, 1]),
                inputs=tf.reshape(rnn_output, [-1, self.hidden_dim]),
                num_sampled=self.sample_size,
                num_classes=self.item_dim)
            self.supervised_loss = tf.reshape(self.supervised_loss, [output_shape[0], output_shape[1]])
            self.supervised_loss = tf.reduce_mean(self.supervised_loss, axis=0)
            self.supervised_loss = tf.reduce_sum(self.supervised_loss)

            self.loss = self.supervised_loss
            #self.loss = 0.5 * self.value_loss + 1.0 * self.policy_loss - 0.1 * self.entropy
            #self.loss = 1.0 * self.supervised_loss + 0.25 * self.value_loss + 0.5 * self.policy_loss - 0.05 * self.entropy

            self.advantages_sum = tf.reduce_sum(self.advantages)

            trainable_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, self.scope)
            gradients = tf.gradients(self.loss, trainable_vars)
            clipped_gradients, _ = tf.clip_by_global_norm(gradients, 5.0)

            self.train_op = optimizer.apply_gradients(zip(clipped_gradients, trainable_vars))


class A3CNetwork(object):
    def __init__(self, scope, optimizer, params):
        self.scope = scope
        with tf.variable_scope(self.scope):
            self.optimizer = optimizer

            self.item_dim = params['item_dim']
            self.output_dim = params['output_dim']
            self.hidden_dim = params['hidden_dim']
            self.batch_dim = params['batch_dim']

            # Actor #
            self.env_state_input = tf.placeholder(tf.int32, shape=[None, None], name='input')
            with tf.device("/cpu:0"):
                env_state_embedding = tf.get_variable(name="state_embedding", shape=[self.item_dim, self.hidden_dim])
                env_state_embedded = tf.nn.embedding_lookup(params=env_state_embedding, ids=self.env_state_input)

            self.keep_prob = tf.placeholder_with_default(0.5, shape=[], name='keep_prob')

            rnn_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_dim, state_is_tuple=True)
            rnn_cell = tf.nn.rnn_cell.DropoutWrapper(rnn_cell, output_keep_prob=self.keep_prob)

            self.length = length(self.env_state_input)

            rnn_output, (rnn_c, rnn_h) = tf.nn.dynamic_rnn(
                inputs=env_state_embedded,
                cell=rnn_cell,
                dtype=tf.float32,
                initial_state=rnn_cell.zero_state(self.batch_dim, dtype=tf.float32),
                sequence_length=self.length
            )
            self.output_shape = output_shape = tf.shape(rnn_output)

            # Probability distribution on the candidate actions a for s #

            self.w = tf.get_variable("w", [self.item_dim, self.hidden_dim], dtype=tf.float32)
            self.b = tf.get_variable("b", [self.item_dim], dtype=tf.float32)

            self.policy_log_prob_output = tf.matmul(tf.reshape(rnn_output, [-1, self.hidden_dim]), self.w, transpose_b=True)
            self.policy_log_prob_output = tf.nn.bias_add(self.policy_log_prob_output, self.b)
            self.policy_log_prob_output = tf.reshape(self.policy_log_prob_output, [output_shape[0], output_shape[1], self.item_dim])
            self.policy_prob_output = tf.nn.softmax(self.policy_log_prob_output)

            # Expected reward of the current state s #
            self.value_output = slim.fully_connected(
                inputs=rnn_output,
                num_outputs=1,
                activation_fn=None,
                weights_initializer=normalized_columns_initializer(1.0),
                biases_initializer=None
            )

            # Critic #
            self.teacher_estimation = tf.placeholder(tf.float32, [None, None, None], name='teacher_estimation')
            self.sv_target = tf.placeholder(tf.int32, [self.batch_dim, None], name='target')
            shape = tf.shape(self.sv_target)

            with tf.device("/cpu:0"):
                self.teacher_loss = tf.nn.softmax_cross_entropy_with_logits(
                    labels=self.teacher_estimation,
                    logits=self.policy_log_prob_output
                )
            self.teacher_loss = tf.reduce_mean(self.teacher_loss, axis=0)
            self.teacher_loss = tf.reduce_sum(self.teacher_loss)

            self.sv_loss = tf.contrib.seq2seq.sequence_loss(
                logits=self.policy_log_prob_output,
                targets=self.sv_target,
                weights=tf.ones(shape=shape),
                average_across_timesteps=False,
                average_across_batch=True,
            )
            self.sv_loss = tf.reduce_sum(self.sv_loss)

            self.actions = tf.placeholder(shape=[None, None], dtype=tf.int32, name='actions')
            actions = tf.one_hot(self.actions, self.output_dim, dtype=tf.float32)

            self.value_target = tf.placeholder(shape=[None, None], dtype=tf.float32, name='value_target')
            self.advantages = tf.placeholder(shape=[None, None], dtype=tf.float32, name='advantages')

            #self.policy_estimate = tf.reduce_sum(tf.multiply(self.policy_prob_output, actions), axis=2)
            with tf.device("/cpu:0"):
                self.policy_estimate = tf.reduce_sum(tf.multiply(self.policy_log_prob_output, actions), axis=2)

            # Loss functions.
            value_output = tf.reshape(self.value_output, tf.shape(self.value_target))
            self.value_loss = 0.5 * tf.reduce_sum(tf.square(self.value_target - value_output))
            self.policy_loss = - tf.reduce_sum(self.policy_estimate * self.advantages)
            self.entropy = - tf.reduce_sum(self.policy_log_prob_output * self.policy_prob_output)
            #self.loss = 0.5 * self.value_loss + 1.0 * self.policy_loss - 0.1 * self.entropy
            #self.loss = self.sv_loss + 0.5 * self.value_loss + 1.0 * self.policy_loss - 0.1 * self.entropy
            #self.loss = self.teacher_loss
            self.loss = self.sv_loss

            self.advantages_sum = tf.reduce_sum(self.advantages)

            local_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, self.scope)

            gradients = tf.gradients(self.loss, local_vars)
            clipped_gradients, _ = tf.clip_by_global_norm(gradients, 5.0)

            self.train_op = optimizer.apply_gradients(zip(clipped_gradients, local_vars))


class AsyncA3CNetwork(object):
    def __init__(self, scope, optimizer, params):
        self.scope = scope
        with tf.variable_scope(self.scope):
            self.optimizer = optimizer

            self.item_dim = params['item_dim']
            self.output_dim = params['output_dim']
            self.hidden_dim = params['hidden_dim']
            self.batch_dim = params['batch_dim']

            # Actor #
            self.env_state_input = tf.placeholder(tf.int32, shape=[None, None], name='input')
            with tf.device("/cpu:0"):
                env_state_embedding = tf.get_variable(name="state_embedding", shape=[self.item_dim, self.hidden_dim])
                env_state_embedded = tf.nn.embedding_lookup(params=env_state_embedding, ids=self.env_state_input)

            rnn_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_dim, state_is_tuple=True)
            rnn_cell = tf.nn.rnn_cell.DropoutWrapper(rnn_cell, output_keep_prob=0.5)

            c_init = np.zeros((self.batch_dim, rnn_cell.state_size.c), np.float32)  # Tuple of form (1, x), where 1 is needed to match 2D requirement of linear transformation
            h_init = np.zeros((self.batch_dim, rnn_cell.state_size.h), np.float32)
            self.rnn_zero_state = [c_init, h_init]

            self.c_input = tf.placeholder(tf.float32, [self.batch_dim, rnn_cell.state_size.c])
            self.h_input = tf.placeholder(tf.float32, [self.batch_dim, rnn_cell.state_size.h])
            state_input = tf.nn.rnn_cell.LSTMStateTuple(self.c_input, self.h_input)

            self.length = length(self.env_state_input)

            rnn_output, (rnn_c, rnn_h) = tf.nn.dynamic_rnn(
                inputs=env_state_embedded,
                cell=rnn_cell,
                dtype=tf.float32,
                initial_state=state_input,
                sequence_length=self.length
            )

            self.rnn_state_output = (rnn_c, rnn_h)

            # Probability distribution on the candidate actions a for s #
            # TODO: Check for correctness
            self.policy_log_prob_output = slim.fully_connected(
                inputs=rnn_output,
                num_outputs=self.output_dim,
                activation_fn=None,
                weights_initializer=normalized_columns_initializer(0.01),
                biases_initializer=None
            )
            self.policy_prob_output = tf.nn.softmax(self.policy_log_prob_output)
            self.policy_log_prob_output = tf.nn.log_softmax(self.policy_log_prob_output)

            # Expected reward of the current state s #
            self.value_output = slim.fully_connected(
                inputs=rnn_output,
                num_outputs=1,
                activation_fn=None,
                weights_initializer=normalized_columns_initializer(1.0),
                biases_initializer=None
            )

            # Critic #
            if self.scope != 'global':
                self.teacher_estimation = tf.placeholder(tf.float32, [None, None, None], name='teacher_estimation')
                self.sv_target = tf.placeholder(tf.int32, [self.batch_dim, None], name='target')
                shape = tf.shape(self.sv_target)

                self.teacher_loss = tf.nn.softmax_cross_entropy_with_logits(
                    labels=self.teacher_estimation,
                    logits=self.policy_log_prob_output
                )
                self.teacher_loss = tf.reduce_mean(self.teacher_loss, axis=0)
                self.teacher_loss = tf.reduce_sum(self.teacher_loss)

                self.sv_loss = tf.contrib.seq2seq.sequence_loss(
                    logits=self.policy_log_prob_output,
                    targets=self.sv_target,
                    weights=tf.ones(shape=shape),
                    average_across_timesteps=False,
                    average_across_batch=True,
                )
                self.sv_loss = tf.reduce_sum(self.sv_loss)

                self.actions = tf.placeholder(shape=[None, None], dtype=tf.int32, name='actions')
                actions = tf.one_hot(self.actions, self.output_dim, dtype=tf.float32)

                self.value_target = tf.placeholder(shape=[None, None], dtype=tf.float32, name='value_target')
                self.advantages = tf.placeholder(shape=[None, None], dtype=tf.float32, name='advantages')

                #self.policy_estimate = tf.reduce_sum(tf.multiply(self.policy_prob_output, actions), axis=2)
                self.policy_estimate = tf.reduce_sum(tf.multiply(self.policy_log_prob_output, actions), axis=2)

                # Loss functions.
                value_output = tf.reshape(self.value_output, tf.shape(self.value_target))
                self.value_loss = 0.5 * tf.reduce_sum(tf.square(self.value_target - value_output))
                self.policy_loss = - tf.reduce_sum(self.policy_estimate * self.advantages)
                self.entropy = - tf.reduce_sum(self.policy_log_prob_output * self.policy_prob_output)
                #self.loss = 0.5 * self.value_loss + 1.0 * self.policy_loss - 0.1 * self.entropy
                self.loss = self.sv_loss + 0.5 * self.value_loss + 1.0 * self.policy_loss - 0.1 * self.entropy
                #self.loss = self.teacher_loss
                #self.loss = self.sv_loss

                self.advantages_sum = tf.reduce_sum(self.advantages)

                local_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, self.scope)
                global_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, 'global')

                gradients = tf.gradients(self.loss, local_vars)
                clipped_gradients, _ = tf.clip_by_global_norm(gradients, 5.0)

                self.train_op = optimizer.apply_gradients(zip(clipped_gradients, global_vars))
