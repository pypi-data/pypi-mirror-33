import collections

import numpy as np
import tensorflow as tf
import time

from rec_rnn_a3c.src.a3c_network import AsyncA3CNetwork, A3CNetwork, MetaA3CNetwork, MetaA3CNetwork0
from rec_rnn_a3c.src.util import update_target_graph, discount

Rollout = collections.namedtuple("Rollout", ["state", "action", "reward", "teacher_reward", "target", "value"])


class MetaA3CModel(object):
    def __init__(self, name, optimizer, params, global_episodes):
        self.name = "model_" + str(name)
        self.optimizer = optimizer
        self.global_episodes = global_episodes
        self.summary_writer = tf.summary.FileWriter("train")

        self.increment = self.global_episodes.assign_add(1)

        self.a3c_network = MetaA3CNetwork(scope=self.name, optimizer=optimizer, params=params)

        self.full_rl = params['full_rl']
        self.unfold_dim = params['unfold_dim']
        self.batch_dim = params['batch_dim']

    def train(self, rollout, sess, gamma, bootstrap_value):
        state = rollout.state
        actions = rollout.action
        reward = rollout.reward
        target = rollout.target
        value = np.reshape(rollout.value, newshape=[self.batch_dim, -1])

        prev_actions = np.append(np.zeros(shape=[self.batch_dim, 1]), actions[:, :-1], axis=1)
        prev_reward = np.append(np.zeros(shape=[self.batch_dim, 1]), reward[:, :-1], axis=1)

        discounted_reward = discount(reward, gamma)
        value = np.append(value, np.zeros(shape=[self.batch_dim, 1]), axis=1)
        advantage = reward + gamma * value[:, 1:] - value[:, :-1]
        advantage = discount(advantage, gamma)

        feed_dict = {
            self.a3c_network.state: state,
            self.a3c_network.actions: actions,
            self.a3c_network.value_target: discounted_reward,
            self.a3c_network.advantages: advantage,
            self.a3c_network.supervised_target: target,
        }

        fetches = [
            self.a3c_network.policy_prob_output,
            self.a3c_network.value_loss,
            self.a3c_network.entropy,
            self.a3c_network.policy_loss,
            self.a3c_network.supervised_loss,
            self.a3c_network.advantages_sum,
            self.a3c_network.train_op,
        ]

        policy_prob_output, value_loss, entropy, policy_loss, sv_loss, advantages_sum, _ = sess.run(
            fetches=fetches,
            feed_dict=feed_dict
        )
        return value_loss, entropy, policy_loss, sv_loss, advantages_sum, policy_prob_output

    def supervised_train(self, rollout, sess, gamma, bootstrap_value):
        state = rollout.state
        actions = rollout.action
        reward = rollout.reward
        target = rollout.target

        prev_actions = np.append(np.zeros(shape=[self.batch_dim, 1]), actions[:, :-1], axis=1)
        prev_reward = np.append(np.zeros(shape=[self.batch_dim, 1]), reward[:, :-1], axis=1)

        feed_dict = {
            self.a3c_network.state: state,
            self.a3c_network.supervised_target: target,
        }

        fetches = [
            self.a3c_network.supervised_loss,
            self.a3c_network.train_op,
        ]

        supervised_loss, _ = sess.run(
            fetches=fetches,
            feed_dict=feed_dict
        )
        return supervised_loss


    def fit(self,
            gamma,
            sess,
            iterator,
            iteration,
            num_iterations,
            iterator_feed_dict):
        episode_count = sess.run(self.global_episodes)

        tf.logging.info("Starting worker %s" % self.name)
        with sess.as_default(), sess.graph.as_default():
            sess.run(iterator.initializer, feed_dict=iterator_feed_dict)
            next_element = iterator.get_next()

        episode_rewards = 0.0
        episode_supervised_loss = 0.0
        episode_policy_loss = 0.0
        episode_value_loss = 0.0

        start = time.time()
        for i in range(iteration, num_iterations):
            try:
                with sess.as_default(), sess.graph.as_default():
                    sequence, label_sequence = sess.run(next_element)
                    sequence_shape = np.shape(sequence)

                    actions = np.zeros([self.batch_dim, 1], dtype=np.int32)
                    reward = np.zeros([self.batch_dim, 1], dtype=np.float32)
                    values = np.asarray([], np.float32)

                    padded_sequence = np.zeros([self.batch_dim, self.unfold_dim])
                    padded_sequence[:sequence.shape[0], :sequence.shape[1]] = sequence

                    padded_label_sequence = np.zeros([self.batch_dim, self.unfold_dim])
                    padded_label_sequence[:label_sequence.shape[0], :label_sequence.shape[1]] = label_sequence

                    step_rollout = Rollout(
                        state=sequence,
                        action=label_sequence,
                        reward=reward,
                        teacher_reward=None,
                        target=label_sequence,
                        value=values)

                    if self.full_rl:
                        value_loss, entropy, policy_loss, supervised_loss, advantages_sum, policy_prob_output = self.train(
                            step_rollout, sess, gamma, 0.0)

                        episode_rewards += np.mean(reward)
                        episode_supervised_loss += np.mean(supervised_loss)
                        episode_policy_loss += np.mean(policy_loss)
                        episode_value_loss += np.mean(value_loss)
                    else:
                        supervised_loss = self.supervised_train(step_rollout, sess, gamma, 0.0)

                        episode_rewards += np.mean(reward)
                        episode_supervised_loss += np.mean(supervised_loss)
                        episode_policy_loss += 0.0
                        episode_value_loss += 0.0

                    if i % 50 == 0 and i != 0:
                        if self.full_rl:
                            action_overlap = np.equal(np.reshape(actions, [-1]), np.reshape(target_split, [-1]))
                            action_overlap = np.reshape(action_overlap, newshape=[self.a3c_network.batch_dim, -1])

                            estimated_action_probabilities = np.reshape([policy_prob_output[:, k, actions[:, k]]
                                                                         for k in range(np.shape(actions)[1])], [1, -1])
                            target_action_probabilities = np.reshape([policy_prob_output[:, k, target_split[:, k]]
                                                                      for k in range(np.shape(target_split)[1])],
                                                                     [1, -1])

                            estimated_action_probabilities = np.mean(estimated_action_probabilities)
                            target_action_probabilities = np.mean(target_action_probabilities)
                            action_overlap = np.mean(action_overlap)
                        else:
                            estimated_action_probabilities = float('nan')
                            target_action_probabilities = float('nan')
                            action_overlap = float('nan')

                        tf.logging.info("%s  -- Ep: [%d/%d]@[%d] -- "
                                        "Reward: %s | "
                                        "C.E. Loss: %.3f | "
                                        "Val. Loss: %.3f | "
                                        "Pol. Loss: %.3f | "
                                        "Est. Prob: %s | "
                                        "Rew. Prob: %s | "
                                        "Action Overlap: %s |"
                                        "Time: %s" %
                                        (self.name,
                                         i + 1,
                                         num_iterations,
                                         episode_count,
                                         episode_rewards / (i + 1),
                                         episode_supervised_loss / (i + 1),
                                         episode_value_loss / (i + 1),
                                         episode_policy_loss / (i + 1),
                                         estimated_action_probabilities,
                                         target_action_probabilities,
                                         action_overlap,
                                         time.time() - start))

                        start = time.time()
            except tf.errors.OutOfRangeError:
                break

        if self.full_rl:
            action_overlap = np.equal(np.reshape(actions, [-1]), np.reshape(target_split, [-1]))
            action_overlap = np.reshape(action_overlap, newshape=[self.a3c_network.batch_dim, -1])

            estimated_action_probabilities = np.reshape([policy_prob_output[:, k, actions[:, k]]
                                                         for k in range(np.shape(actions)[1])], [1, -1])
            target_action_probabilities = np.reshape([policy_prob_output[:, k, target_split[:, k]]
                                                      for k in range(np.shape(target_split)[1])],
                                                     [1, -1])

            estimated_action_probabilities = np.mean(estimated_action_probabilities)
            target_action_probabilities = np.mean(target_action_probabilities)
            action_overlap = np.mean(action_overlap)
        else:
            estimated_action_probabilities = float('nan')
            target_action_probabilities = float('nan')
            action_overlap = float('nan')

        tf.logging.info("%s  -- Ep: [%d/%d]@[%d] -- "
                        "Reward: %s | "
                        "C.E. Loss: %.3f | "
                        "Val. Loss: %.3f | "
                        "Pol. Loss: %.3f | "
                        "Est. Prob: %s | "
                        "Rew. Prob: %s | "
                        "Action Overlap: %s" %
                        (self.name,
                         i,
                         num_iterations,
                         episode_count,
                         episode_rewards / (i + 1),
                         episode_supervised_loss / (i + 1),
                         episode_value_loss / (i + 1),
                         episode_policy_loss / (i + 1),
                         estimated_action_probabilities,
                         target_action_probabilities,
                         action_overlap))
        sess.run(self.increment)
        episode_count += 1

    def predict(self, sequence, targets, sess):
        with sess.as_default(), sess.graph.as_default():
            actions = np.zeros([self.batch_dim, 1], dtype=np.int32)
            reward = np.zeros([self.batch_dim, 1], dtype=np.float32)
            values = np.asarray([], np.float32)

            padded_sequence = np.zeros([self.batch_dim, self.unfold_dim])
            padded_sequence[:sequence.shape[0], :sequence.shape[1]] = sequence

            padded_label_sequence = np.zeros([self.batch_dim, self.unfold_dim])
            padded_label_sequence[:targets.shape[0], :targets.shape[1]] = targets

            feed_dict = {
                self.a3c_network.state: padded_sequence,
                self.a3c_network.supervised_target: padded_label_sequence
            }

            fetches = [
                self.a3c_network.policy_logit_output,
                self.a3c_network.value_output,
            ]

            policy_logit_dist, value_output = sess.run(
                feed_dict=feed_dict,
                fetches=fetches
            )

            values = np.append(values, value_output)
            values = np.reshape(values, newshape=[self.a3c_network.batch_dim, -1])

            actions_ = np.argmax(policy_logit_dist, axis=2)

            actions = np.append(actions, actions_)
            actions = np.reshape(actions, newshape=[self.a3c_network.batch_dim, -1])

            reward_ = actions_ == targets
            reward = np.append(reward, reward_)
            reward = np.reshape(reward, newshape=[self.a3c_network.batch_dim, -1])

            return actions[:, 1:], reward[:, 1:]


class A3CModel(object):
    def __init__(self, name, optimizer, params, global_episodes):
        self.name = "model_" + str(name)
        self.optimizer = optimizer
        self.global_episodes = global_episodes
        self.summary_writer = tf.summary.FileWriter("train")

        self.increment = self.global_episodes.assign_add(1)

        self.local_a3c_network = A3CNetwork(scope=self.name, optimizer=optimizer, params=params)

        self.use_pretrained_rnn = params['use_pretrained_rnn']
        self.unfold_dim = params['unfold_dim']

    def train(self, rollout, sess, gamma, bootstrap_value):
        env_state = rollout.env_state
        action_estimate = rollout.action_estimate
        reward = rollout.reward
        teacher_estimation = rollout.teacher_estimation
        action_target = rollout.action_target
        value_estimate = np.squeeze(rollout.value_estimate, axis=2)

        # Step 1: Calculate Discounted rewards (Act as an estimator for Q(s,a) #
        # bootstrap_value as an estimate of future reward #
        reward_bootstrapped = reward
        # reward_bootstrapped = np.append(reward, bootstrap_value, axis=1)
        # TODO: Check how this should work
        reward_bootstrapped = discount(reward_bootstrapped, gamma)
        # print("Bootstrap Reward: %s" % reward_bootstrapped)

        # Step 2: Calculate Advantage based on "Generalized Advantage Estimation (Schulman et al., 2016)" #
        value_bootstrapped = np.append(value_estimate, bootstrap_value, axis=1)
        advantage = reward + 0.01 * value_bootstrapped[:, 1:] - value_bootstrapped[:, :-1]
        # advantage = reward + gamma * value_bootstrapped[:, 1:] - value_bootstrapped[:, :-1]
        # advantage = discount(advantage, gamma)

        # Step 3: Step into AC-Network to train #
        feed_dict = {
            self.local_a3c_network.env_state_input: env_state,
            self.local_a3c_network.actions: action_estimate,
            self.local_a3c_network.value_target: reward_bootstrapped,
            self.local_a3c_network.advantages: advantage,

            self.local_a3c_network.sv_target: action_target,
            self.local_a3c_network.teacher_estimation: teacher_estimation
        }

        fetches = [
            self.local_a3c_network.value_loss,
            self.local_a3c_network.entropy,
            self.local_a3c_network.policy_loss,
            self.local_a3c_network.advantages_sum,
            self.local_a3c_network.train_op,
        ]

        value_loss, entropy, policy_loss, advantages_sum, train_op = sess.run(
            fetches=fetches,
            feed_dict=feed_dict
        )
        # TODO: Normalize some with batch_size * unfold_size (?)
        return value_loss, entropy, policy_loss, advantages_sum

    def predict(self, sequence, sess):
        with sess.as_default(), sess.graph.as_default():
            feed_dict = {
                self.local_a3c_network.keep_prob: 1.0,
                self.local_a3c_network.env_state_input: sequence,
            }

            fetches = [
                self.local_a3c_network.policy_log_prob_output,
                self.local_a3c_network.policy_prob_output,
                self.local_a3c_network.value_output,
            ]

            # Step 1: Calculate Policy Output (Prob. Dist. over Actions) & Value Output (Estimation of "goodness") #
            policy_log_prob_output, policy_prob_output, value_output = sess.run(
                feed_dict=feed_dict,
                fetches=fetches
            )
            # TODO: Correct output
            return policy_prob_output, value_output

    def reward(self,
               sequence,
               actual_action,
               predicted_action,
               value,
               reward,
               sess,
               gamma):
        with sess.as_default(), sess.graph.as_default():
            step_rollout = Rollout(
                env_state=sequence,
                action_estimate=predicted_action,
                reward=reward,
                teacher_estimation=np.zeros(shape=[1, 1, 11]),
                action_target=actual_action,
                value_estimate=value)

            # Step 4: Since we don't know the true final return, we "bootstrap" from current value estimation
            feed_dict = {
                self.local_a3c_network.env_state_input: sequence,
            }
            value_output = sess.run(
                fetches=self.local_a3c_network.value_output,
                feed_dict=feed_dict
            )[:, -1, :]

            # Step 5: Calculate Loss based on Action, Cur. Obs., Reward, Fut. Obs., Value and Bootstrap Value #
            value_loss, entropy, policy_loss, advantages_sum = self.train(step_rollout, sess, gamma, value_output)

    def fit(self,
            gamma,
            supervised_model,
            sess,
            iterator,
            iteration,
            num_iterations,
            iterator_feed_dict):
        episode_count = sess.run(self.global_episodes)

        # TODO: Include logging
        tf.logging.info("Starting worker %s" % self.name)
        with sess.as_default(), sess.graph.as_default():
            sess.run(iterator.initializer, feed_dict=iterator_feed_dict)

            next_element = iterator.get_next()

        all_rewards = []

        for current_step in range(iteration, num_iterations):
            try:
                with sess.as_default(), sess.graph.as_default():
                    sequence, label_sequence = sess.run(next_element)

                    num_sequence_splits = np.max([1, np.shape(label_sequence)[1] // self.unfold_dim])

                    step_reward = 0.0

                    for split in range(num_sequence_splits):
                        state_split = sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]
                        target_split = label_sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]

                        feed_dict = {
                            self.local_a3c_network.env_state_input: state_split,
                        }

                        fetches = [
                            self.local_a3c_network.policy_log_prob_output,
                            self.local_a3c_network.policy_prob_output,
                            self.local_a3c_network.value_output,
                        ]

                        # Step 1: Calculate Policy Output (Prob. Dist. over Actions) & Value Output (Estimation of "goodness") #
                        policy_log_prob_output, policy_prob_output, value_output = sess.run(
                            feed_dict=feed_dict,
                            fetches=fetches
                        )

                        # Step 2: Select Action epsilon-greedily #
                        actions = np.argmax(policy_prob_output, axis=2)
                        actions_shape = np.shape(actions)
                        actions = np.reshape(actions, [-1])
                        mask = np.random.choice([False, True], np.shape(actions), p=[0.95, 0.05])
                        actions[mask] = np.random.randint(0, self.local_a3c_network.item_dim, size=np.sum(mask))
                        actions = np.reshape(actions, actions_shape)

                        # Step 3: Calculate reward #
                        reward_feed_dict = {
                            supervised_model.reward_network.input: state_split,
                        }

                        reward_fetches = [
                            supervised_model.reward_network.logit_dist,
                            supervised_model.reward_network.prob_dist,
                        ]

                        reward_action_log_probs, reward_action_probs = sess.run(
                            feed_dict=reward_feed_dict,
                            fetches=reward_fetches
                        )
                        reward = [reward_action_probs[:, i, actions[:, i]] for i in range(np.shape(actions)[1])]
                        reward = np.reshape(reward, newshape=[self.local_a3c_network.batch_dim, -1])

                        step_reward += np.mean(reward)

                        step_rollout = Rollout(
                            env_state=state_split,
                            action_estimate=actions,
                            reward=reward,
                            teacher_estimation=reward_action_probs,
                            action_target=target_split,
                            value_estimate=value_output)

                        # Step 4: Since we don't know the true final return, we "bootstrap" from current value estimation
                        feed_dict[self.local_a3c_network.env_state_input] = target_split
                        value_output = sess.run(
                            fetches=self.local_a3c_network.value_output,
                            feed_dict=feed_dict
                        )
                        value_output = value_output[:, -1, :]

                        # Step 5: Calculate Loss based on Action, Cur. Obs., Reward, Fut. Obs., Value and Bootstrap Value #
                        value_loss, entropy, policy_loss, advantages_sum = self.train(step_rollout, sess, gamma,
                                                                                      value_output)

                        action_overlap = np.equal(np.reshape(actions, [-1]), np.reshape(target_split, [-1]))
                        action_overlap = np.reshape(action_overlap, newshape=[self.local_a3c_network.batch_dim, -1])

                        estimated_action_probabilities = np.reshape([policy_prob_output[:, i, actions[:, i]]
                                                                     for i in range(np.shape(actions)[1])], [1, -1])
                        target_action_probabilities = np.reshape([policy_prob_output[:, i, target_split[:, i]]
                                                                  for i in range(np.shape(target_split)[1])], [1, -1])

                        pass
            except tf.errors.OutOfRangeError:
                break

        all_rewards.append(step_reward)

        # tf.logging.info(actions)
        tf.logging.info("%s  -- Ep: %d[%d] -- "
                        "Reward: %s | "
                        "Val. Loss: %s | "
                        "Pol. Loss: %s | "
                        "Est. Prob: %s | "
                        "Rew. Prob: %s | "
                        "Action Overlap: %s" %
                        (self.name,
                         episode_count,
                         iteration,
                         np.mean(all_rewards[-5:]),
                         value_loss,
                         policy_loss,
                         np.mean(estimated_action_probabilities),
                         np.mean(target_action_probabilities),
                         np.mean(action_overlap)))

        sess.run(self.increment)
        episode_count += 1


class AsyncA3CModel(object):
    def __init__(self, name, optimizer, global_a3c_network, params, global_episodes, saver=None):
        self.name = "model_" + str(name)
        self.optimizer = optimizer
        self.global_episodes = global_episodes
        self.saver = saver
        self.summary_writer = tf.summary.FileWriter("train")

        self.increment = self.global_episodes.assign_add(1)

        self.global_a3c_network = global_a3c_network
        self.local_a3c_network = AsyncA3CNetwork(scope=self.name, optimizer=optimizer, params=params)

        self.update_local_ops = update_target_graph('global', self.name)

        self.use_pretrained_rnn = params['use_pretrained_rnn']
        self.unfold_dim = params['unfold_dim']

    def train(self, rollout, sess, gamma, bootstrap_value):
        env_state = rollout.env_state
        action_estimate = rollout.action_estimate
        reward = rollout.reward
        teacher_estimation = rollout.teacher_estimation
        action_target = rollout.action_target
        value_estimate = np.squeeze(rollout.value_estimate, axis=2)

        # Step 1: Calculate Discounted rewards (Act as an estimator for Q(s,a) #
        # bootstrap_value as an estimate of future reward #
        reward_bootstrapped = reward
        # reward_bootstrapped = np.append(reward, bootstrap_value, axis=1)
        # TODO: Check how this should work
        # reward_bootstrapped = discount(reward_bootstrapped, gamma)

        # Step 2: Calculate Advantage based on "Generalized Advantage Estimation (Schulman et al., 2016)" #
        value_bootstrapped = np.append(value_estimate, bootstrap_value, axis=1)
        advantage = reward + 0.01 * value_bootstrapped[:, 1:] - value_bootstrapped[:, :-1]
        # advantage = reward + gamma * value_bootstrapped[:, 1:] - value_bootstrapped[:, :-1]
        # advantage = discount(advantage, gamma)

        # Step 3: Step into AC-Network to train #
        feed_dict = {
            self.local_a3c_network.env_state_input: env_state,
            self.local_a3c_network.c_input: self.rnn_state_c,
            self.local_a3c_network.h_input: self.rnn_state_h,
            self.local_a3c_network.actions: action_estimate,
            self.local_a3c_network.value_target: reward_bootstrapped,
            self.local_a3c_network.advantages: advantage,

            self.local_a3c_network.sv_target: action_target,
            self.local_a3c_network.teacher_estimation: teacher_estimation
        }

        fetches = [
            self.local_a3c_network.value_loss,
            self.local_a3c_network.entropy,
            self.local_a3c_network.policy_loss,
            self.local_a3c_network.advantages_sum,
            self.local_a3c_network.train_op,
        ]

        value_loss, entropy, policy_loss, advantages_sum, train_op = sess.run(
            fetches=fetches,
            feed_dict=feed_dict
        )
        # TODO: Normalize some with batch_size * unfold_size (?)
        return value_loss, entropy, policy_loss, advantages_sum

    def predict(self, input_seq, gamma, reward_worker, sess):
        sess.run(self.update_local_ops)
        feed_dict = {
            self.local_a3c_network.env_state_input: input_seq,
            self.local_a3c_network.c_input: self.rnn_state_c,
            self.local_a3c_network.h_input: self.rnn_state_h,
        }

        fetches = [
            self.local_a3c_network.policy_log_prob_output,
            self.local_a3c_network.policy_prob_output,
            self.local_a3c_network.value_output,
            self.local_a3c_network.rnn_state_output,
        ]

        # Step 1: Calculate Policy Output (Prob. Dist. over Actions) & Value Output (Estimation of "goodness") #
        policy_log_prob_output, policy_prob_output, value_output, (self.rnn_state_c, self.rnn_state_h) = sess.run(
            feed_dict=feed_dict,
            fetches=fetches
        )

        # Step 2: Select Action epsilon-greedily #
        actions = np.argmax(policy_prob_output, axis=2)
        actions_shape = np.shape(actions)
        actions = np.reshape(actions, [-1])
        mask = np.random.choice([False, True], np.shape(actions), p=[0.95, 0.05])
        actions[mask] = np.random.randint(0, self.local_a3c_network.item_dim, size=np.sum(mask))
        actions = np.reshape(actions, actions_shape)

        return actions, value_output

    def online_train(self, gamma, input_seq, target_seq, sess, reward_worker, actions, value):
        # Step 3: Calculate reward #
        reward_feed_dict = {
            reward_worker.reward_network.input: input_seq,
            reward_worker.reward_network.c_input: self.rnn_state_c,
            reward_worker.reward_network.h_input: self.rnn_state_h,
        }

        reward_fetches = [
            reward_worker.reward_network.action_logit_dist,
            reward_worker.reward_network.action_prob_dist,
        ]

        reward_action_log_probs, reward_action_probs = sess.run(
            feed_dict=reward_feed_dict,
            fetches=reward_fetches
        )
        reward = [reward_action_probs[:, i, actions[:, i]] for i in range(np.shape(actions)[1])]
        reward = np.reshape(reward, newshape=[self.local_a3c_network.batch_dim, -1])

        step_rollout = Rollout(
            env_state=input_seq,
            action_estimate=actions,
            reward=reward,
            action_target=target_seq,
            value_estimate=value)

        # Step 4: Since we don't know the true final return, we "bootstrap" from current value estimation
        feed_dict = {
            self.local_a3c_network.env_state_input: target_seq,
            self.local_a3c_network.c_input: self.rnn_state_c,
            self.local_a3c_network.h_input: self.rnn_state_h,
        }

        value_output = sess.run(
            fetches=self.local_a3c_network.value_output,
            feed_dict=feed_dict
        )[:, -1, :]

        # Step 5: Calculate Loss based on Action, Cur. Obs., Reward, Fut. Obs., Value and Bootstrap Value #

        self.train(step_rollout, sess, gamma, value_output)
        sess.run(self.update_local_ops)

    def fit(self,
            gamma,
            supervised_model,
            sess,
            coordinator,
            iterator,
            iteration,
            num_iterations,
            iterator_feed_dict,
            supervised_session,
            global_a3c_session):
        episode_count = sess.run(self.global_episodes)

        next_element = iterator.get_next()

        # TODO: Include logging
        print("Starting worker %s" % self.name)
        while not coordinator.should_stop() and episode_count < 100:
            # TODO: Reset states for every episode?
            if self.use_pretrained_rnn:
                rnn_state_c, rnn_state_h = (supervised_model.rnn_state_c, supervised_model.rnn_state_h)
            else:
                rnn_state_c, rnn_state_h = self.local_a3c_network.rnn_zero_state

            self.rnn_state_c = rnn_state_c
            self.rnn_state_h = rnn_state_h

            with sess.as_default(), sess.graph.as_default():
                sess.run(self.update_local_ops)
                sess.run(iterator.initializer, feed_dict=iterator_feed_dict)

            all_rewards = []

            for current_step in range(iteration, num_iterations):
                try:
                    with sess.as_default(), sess.graph.as_default():
                        sequence, label_sequence = sess.run(next_element)

                        num_sequence_splits = np.max([1, np.shape(label_sequence)[1] // self.unfold_dim])

                        step_reward = 0.0

                        for split in range(num_sequence_splits):
                            state_split = sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]
                            target_split = label_sequence[:, split * self.unfold_dim:(split + 1) * self.unfold_dim]

                            feed_dict = {
                                self.local_a3c_network.env_state_input: state_split,
                                self.local_a3c_network.c_input: self.rnn_state_c,
                                self.local_a3c_network.h_input: self.rnn_state_h,
                            }

                            fetches = [
                                self.local_a3c_network.policy_log_prob_output,
                                self.local_a3c_network.policy_prob_output,
                                self.local_a3c_network.value_output,
                                self.local_a3c_network.rnn_state_output,
                            ]

                            # Step 1: Calculate Policy Output (Prob. Dist. over Actions) & Value Output (Estimation of "goodness") #
                            policy_log_prob_output, policy_prob_output, value_output, (
                                self.rnn_state_c, self.rnn_state_h) = sess.run(
                                feed_dict=feed_dict,
                                fetches=fetches
                            )
                    with supervised_session.as_default(), supervised_session.graph.as_default():

                        # Step 2: Select Action epsilon-greedily #
                        actions = np.argmax(policy_prob_output, axis=2)
                        actions_shape = np.shape(actions)
                        actions = np.reshape(actions, [-1])
                        mask = np.random.choice([False, True], np.shape(actions), p=[0.95, 0.05])
                        actions[mask] = np.random.randint(0, self.local_a3c_network.item_dim, size=np.sum(mask))
                        actions = np.reshape(actions, actions_shape)

                        # Step 3: Calculate reward #
                        reward_feed_dict = {
                            supervised_model.reward_network.input: state_split,
                            supervised_model.reward_network.c_input: self.rnn_state_c,
                            supervised_model.reward_network.h_input: self.rnn_state_h,
                        }

                        reward_fetches = [
                            supervised_model.reward_network.logit_dist,
                            supervised_model.reward_network.prob_dist,
                        ]

                        reward_action_log_probs, reward_action_probs = supervised_session.run(
                            feed_dict=reward_feed_dict,
                            fetches=reward_fetches
                        )
                        reward = [reward_action_probs[:, i, actions[:, i]] for i in range(np.shape(actions)[1])]
                        reward = np.reshape(reward, newshape=[self.local_a3c_network.batch_dim, -1])

                        # For testing only
                        """
                        reward = np.zeros(np.shape(reward))
                        reward[:, 4] = 100
                        """

                        reward_actions = np.argmax(reward_action_log_probs, axis=2)

                        step_reward += np.mean(reward)

                    with sess.as_default(), sess.graph.as_default():
                        step_rollout = Rollout(
                            env_state=state_split,
                            action_estimate=actions,
                            reward=reward,
                            teacher_estimation=reward_action_probs,
                            action_target=target_split,
                            value_estimate=value_output)

                        # Step 4: Since we don't know the true final return, we "bootstrap" from current value estimation
                        feed_dict[self.local_a3c_network.env_state_input] = target_split
                        value_output = sess.run(
                            fetches=self.local_a3c_network.value_output,
                            feed_dict=feed_dict
                        )[:, -1, :]

                        # Step 5: Calculate Loss based on Action, Cur. Obs., Reward, Fut. Obs., Value and Bootstrap Value #
                        value_loss, entropy, policy_loss, advantages_sum = self.train(step_rollout, sess, gamma,
                                                                                      value_output)

                        sess.run(self.update_local_ops)

                        action_overlap = np.equal(np.reshape(actions, [-1]), np.reshape(target_split, [-1]))
                        action_overlap = np.reshape(action_overlap, newshape=[self.local_a3c_network.batch_dim, -1])

                        estimated_action_probabilities = np.reshape([policy_prob_output[:, i, actions[:, i]]
                                                                     for i in range(np.shape(actions)[1])], [1, -1])
                        target_action_probabilities = np.reshape([policy_prob_output[:, i, target_split[:, i]]
                                                                  for i in range(np.shape(target_split)[1])], [1, -1])

                        pass
                except tf.errors.OutOfRangeError:
                    break

            all_rewards.append(step_reward)

            # tf.logging.info(actions)
            tf.logging.info("%s  -- Ep: %d[%d] -- "
                            "Reward: %s | "
                            "Val. Loss: %s | "
                            "Pol. Loss: %s | "
                            "Est. Prob: %s | "
                            "Rew. Prob: %s | "
                            "Action Overlap: %s" %
                            (self.name,
                             episode_count,
                             iteration,
                             np.mean(all_rewards[-5:]),
                             value_loss,
                             policy_loss,
                             np.mean(estimated_action_probabilities),
                             np.mean(target_action_probabilities),
                             np.mean(action_overlap)))

            # TODO: Maybe add break condition

            sess.run(self.increment)
            episode_count += 1
            # TODO: Update network at the end of episode. Necessary in my setting?

            """ TODO 
            summary = tf.Summary()
            summary.value.add(tag='Perf/Reward', simple_value=float(np.mean(self.episode_rewards[-5:])))
            summary.value.add(tag='Losses/Value Loss', simple_value=float(value_loss))
            self.summary_writer.add_summary(summary, episode_count)
            self.summary_writer.flush()
            """
