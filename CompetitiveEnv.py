from GymEnv import KuruveGymEnv

from gym import spaces
import numpy as np


class CompetitiveEnv(KuruveGymEnv):

    def __init__(self, headless=False, observation_size=(64, 64), fps_cap=0, frameskip=0, enable_powerups=False,
                 verbose=0, player2_step=None, player2_reset=None):
        super().__init__(headless, observation_size, fps_cap, frameskip, enable_powerups, verbose)

        self.action_space = spaces.Discrete(3)
        # TODO: Add second channel
        #self.observation_space = spaces.Box(low=0, high=255, dtype=np.uint8, shape=(self.screen_size[0], self.screen_size[1], 3))
        self.observation_space = spaces.Box(low=0, high=255, dtype=np.uint8, shape=(self.screen_size[1], self.screen_size[0], 1))

        self.player2_step = player2_step
        self.player2_reset = player2_reset
        self.player2_obs = None

    def reset(self):
        obs = super().reset()
        obs = self._process_observation(obs)

        self.player2_reset()
        self.player2_obs = obs[1]
        return obs[0]

    def step(self, action):
        p2_action = self.player2_step(self.player2_obs)
        actions = [action, p2_action]
        obs, reward, done, info = super().step(actions)
        obs = self._process_observation(obs)

        self.player2_obs = obs[1]
        reward = reward[0]
        #info = {"total_reward": self.total_reward, "score_difference": self.score_difference}
        info = {}
        return obs[0], reward, done, info

    def render(self, mode="human"):
        raise NotImplementedError

    def close(self):
        super().close()
        print("Game close")

    def seed(self, seed=None):
        raise NotImplementedError

    def _process_observation(self, obs):
        obs = np.dot(obs[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        obs = obs.reshape((2, self.screen_size[1], self.screen_size[0], 1))
        return obs
