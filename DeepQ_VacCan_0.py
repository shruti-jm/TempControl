import random
import gym
import math
import numpy as np
from collections import deque


from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.optimizers import Adam

## Class containing code that works with the gym environment
class DQNSolver():
    def __init__(self, n_episodes=3500, n_win_ticks=999, max_env_steps=None, gamma=1.0, epsilon=1.0, epsilon_min=0.01, epsilon_log_decay=0.995, alpha=0.05, alpha_decay=0.01, batch_size=64, monitor=False, quiet=False):
        self.memory = deque(maxlen=100000)

        self.env = gym.make('VacCan-v0')

        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_log_decay

        # step-size in optimization algorithm
        self.alpha = alpha
        self.alpha_decay = alpha_decay

        self.n_episodes = n_episodes
        self.n_win_ticks = n_win_ticks
        self.batch_size = batch_size
        self.quiet = quiet
        if max_env_steps is not None: self.env._max_episode_steps = max_env_steps

        # Init model
        self.model = Sequential()
        self.model.add(Dense(12, input_dim=2, activation='relu'))
        self.model.add(Dense(24, activation='relu'))
        self.model.add(Dense(35, activation='linear'))
        self.model.compile(loss='mse', optimizer=Adam(lr=self.alpha, decay=self.alpha_decay))

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def choose_action(self, state, epsilon):
        return self.env.action_space.sample() if (np.random.random() <= epsilon) else np.argmax(self.model.predict(state))

    def get_epsilon(self, t):
        return max(self.epsilon_min, min(self.epsilon, 1.0 - math.log10((t + 1) * self.epsilon_decay)))

    def preprocess_state(self, state):
        return np.reshape(state, [1, 2])

    def replay(self, batch_size):
        x_batch, y_batch = [], []
        minibatch = random.sample(self.memory, min(len(self.memory), batch_size))
        for state, action, reward, next_state, done in minibatch:
            y_target = self.model.predict(state)
            y_target[0][action] = reward if done else reward + self.gamma * np.max(self.model.predict(next_state)[0])
            x_batch.append(state[0])
            y_batch.append(y_target[0])

            # fit() uses the optimiser to minimize the loss function
            self.model.fit(np.array(x_batch), np.array(y_batch), batch_size=len(x_batch), verbose=0)
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

    def save(self, name):
        self.model.save_weights(name)

    def load(self, name):
        self.model.load_weights(name)
        self.env.render()

    def run(self):
        scores = deque(maxlen=50)

        for e in range(self.n_episodes):
            state = self.preprocess_state(self.env.reset())
            done = False
            i = 0
            # self.env.render()
            while not done:
                action = self.choose_action(state, self.get_epsilon(e))
                next_state, reward, done, _ = self.env.step(action)
                next_state = self.preprocess_state(next_state)
                self.remember(state, action, reward, next_state, done)
                state = next_state
                i += reward

            scores.append(i)
            mean_score = np.mean(scores)
            if mean_score >= self.n_win_ticks and e > 50:
                if not self.quiet: print('Ran {} episodes. Solved after {} trials'.format(e, e - 50))
                self.save("./vaccan-model0.h5")
                return e - 50

            if e % 50 == 0 and not self.quiet:
                print('[Episode {}] - Mean survival time over last 50 episodes was {} ticks.'.format(e, mean_score))
                self.save("./vaccan-model0.h5")

            self.replay(self.batch_size)

        if not self.quiet:
            print('Did not solve after {} episodes'.format(e))
            self.save("./vaccan-model0.h5")
        return e

if __name__ == '__main__':
    agent = DQNSolver()
    agent.run()
