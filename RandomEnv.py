from GymEnv import KuruveGymEnv

from gym import spaces
import numpy as np


class RandomEnv(KuruveGymEnv):
    """Environment in which the second worm's actions are random."""

    def __init__(self, headless=False, observation_size=(64, 64), fps_cap=0, frameskip=0, enable_powerups=False,
                 verbose=0):
        super().__init__(headless, observation_size, fps_cap, frameskip, enable_powerups, verbose)

        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=0, high=255, dtype=np.uint8,
                                            shape=(self.screen_size[0], self.screen_size[1], 3))

    def reset(self):
        obs = super().reset()
        return obs[0]

    def step(self, action):
        actions = [action, self.action_space.sample()]
        obs, reward, done, info = super().step(actions)
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
