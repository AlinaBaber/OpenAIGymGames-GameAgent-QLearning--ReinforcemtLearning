import gym
import gym.spaces
import numpy as np
import math
import random
import matplotlib.pyplot as plt
from collections import deque

# create the cart-pole environment
env = gym.make('CartPole-v0')


class CartPole():
    def __init__(self, buckets=(1, 1, 6, 3,), n_episodes=5000, solved_t=195,
                 min_epsilon=0.5, min_alpha=0.15, gamma=0.99):
        self.buckets = buckets  # discrete values for each feature space dimension
        # (position, velocity, angle, angular velocity)
        self.n_episodes = n_episodes  # training episodes
        self.min_alpha = min_alpha
        self.min_epsilon = min_epsilon
        self.gamma = gamma  # discount factor
        self.solved_t = solved_t  # lower bound before episode ends

        self.Q_table = np.zeros(self.buckets + (env.action_space.n,))  # action space (left, right)
        print(self.Q_table )

    def discretize_state(self, state):
        upper_bounds = env.observation_space.high  # upper and lower bounds of state dimensions
        lower_bounds = env.observation_space.low

        upper_bounds[1] = 0.5
        upper_bounds[3] = math.radians(50)  # setting manual bounds for velocity and angluar velocity
        lower_bounds[1] = -0.5
        lower_bounds[3] = -math.radians(50)

        # discretizing each input dimension into one of the buckets
        width = [upper_bounds[i] - lower_bounds[i] for i in range(len(state))]
        ratios = [(state[i] - lower_bounds[i]) / width[i] for i in range(len(state))]
        bucket_indices = [int(round(ratios[i] * (self.buckets[i] - 1))) for i in range(len(state))]

        # making the range of indices to [0, bucket_length]
        bucket_indices = [max(0, min(bucket_indices[i], self.buckets[i] - 1)) for i in range(len(state))]

        return tuple(bucket_indices)

    def select_action(self, state, epsilon):
        # implement the epsilon-greedy approach
        if random.random() <= epsilon:
            return env.action_space.sample()  # sample a random action with probability epsilon
        else:
            return np.argmax(self.Q_table[state])  # choose greedy action with hightest Q-value

    def get_epsilon(self, episode_number):
        # choose decaying epsilon in range [min_epsilon, 1]
        return max(self.min_epsilon, min(1, 1 - math.log10((episode_number + 1) / 25)))

    def get_alpha(self, episode_number):
        # choose decaying alpha in range [min_alpha, 1]
        return max(self.min_alpha, min(1, 1 - math.log10((episode_number + 1) / 25)))

    def update_table(self, old_state, action, reward, new_state, alpha):
        # updates the state-action pairs based on future reward
        new_state_Q_value = np.max(self.Q_table[new_state])
        self.Q_table[old_state][action] += alpha * (
                    reward + self.gamma * new_state_Q_value - self.Q_table[old_state][action])

    def run(self):
        # runs episodes until mean reward of last 100 consecutive episodes is atleast self.solved_t
        env.seed(0)
        np.random.seed(0)
        total_epochs, total_penalties = 0, 0
        #counter = 0
        scores = deque(maxlen=200)
        episodes_result = deque(maxlen=200)
        penalties_result = deque(maxlen=100)
        results = []
        for episode in range(self.n_episodes):

            done = False
            alpha = self.get_alpha(episode)
            epsilon = self.get_epsilon(episode)
            epochs, penalties, episode_reward = 0, 0, 0

            #results.append(cartpole.run())
            obs = env.reset()
            curr_state = self.discretize_state(obs)

            while not done:
                #env.render()
                action = self.select_action(curr_state, epsilon)
                obs, reward, done, info = env.step(action)
                new_state = self.discretize_state(obs)

                self.update_table(curr_state, action, reward, new_state, alpha)
                curr_state = new_state
                episode_reward += reward
                print('Reward:', reward)
                if reward != 1:
                     penalties += 1
                print('penalties:', penalties)
                epochs += 1
                total_penalties += penalties
                total_epochs += epochs
            scores.append(episode_reward)
            episodes_result.append(epochs)
            penalties_result.append(total_penalties)
            mean_reward = np.mean(scores)

        if mean_reward > self.solved_t and (episode + 1) >= 100:
            print("Ran {} episodes, solved after {} trials".format(episode + 1, episode + 1 - 100))
            return episode + 1 - 100
        elif (episode + 1) % 50 == 0 and (episode + 1) >= 100:
            print("Episode number: {}, mean reward over past 100 episodes is {}".format(episode + 1, mean_reward))
        else:
            print("Episode {}, reward {}".format(episode + 1, episode_reward))

        print(f"Results after {episode} episodes:")
        print(f"Average timesteps per episode: {total_epochs / episode}")
        print(f"Average Rewards per episode: {np.mean(scores)}")
        print(f"Average penalties per episode: {total_penalties / episode}")
        print("Training finished.\n")
        plt.hist(episodes_result, 50, normed=1, facecolor='g', alpha=0.75)
        plt.xlabel('Episodes required to reach Goal')
        plt.ylabel('Frequency')
        plt.title('Episode Histogram of Cartpole problem solving by Q Learning')
        plt.show()
        plt.hist(scores, 50, normed=1, facecolor='g', alpha=0.75)
        plt.xlabel('Rewards Achieved Per Episode')
        plt.ylabel('Frequency')
        plt.title('Rewards Histogram of Cartpole problem solving by Q Learning')
        plt.show()
        plt.hist(penalties_result, 50, normed=1, facecolor='g', alpha=0.75)
        plt.xlabel('Penalties Per Episode')
        plt.ylabel('Frequency')
        plt.title('Penalties Histogram of Cartpole problem solving by Q Learning')
        plt.show()
        return episodes_result,scores,penalties_result

if __name__ == "__main__":

    cartpole = CartPole()
    cartpole.run()
    results = []
    #results.append(cartpole.run())

    #plt.hist(results, 50, normed=1, facecolor='g', alpha=0.75)
    #plt.xlabel('Episodes required to reach 200')
    #plt.ylabel('Frequency')
    #plt.title('Histogram of Random Search')
    #plt.show()

    print(np.sum(results) / 1000.0)
