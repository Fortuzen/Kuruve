from kuruve.envs.GymEnv import KuruveGymEnv
from kuruve.KurveGame import *

from gym import spaces
import numpy as np
import math


class CompetitiveEnv(KuruveGymEnv):
    """
    Environment for self-play experiments. Two worms (currently).

    """

    def __init__(self, headless=False, observation_size=(64, 64), fps_cap=0, frameskip=0, enable_powerups=False,
                 verbose=0, player2_step=None, player2_reset=None):
        super().__init__(headless, observation_size, fps_cap, frameskip, enable_powerups, verbose)

        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=0, high=255, dtype=np.uint8, shape=(self.screen_size[1], self.screen_size[0], 2))

        self.player2_step = player2_step
        self.player2_reset = player2_reset
        self.player2_obs = None

        self.screen_player_pos_1 = pygame.Surface(self.screen_size)
        self.screen_player_pos_1 = self.screen_player_pos_1.convert(32, 0)

        self.screen_player_pos_2 = pygame.Surface(self.screen_size)
        self.screen_player_pos_2 = self.screen_player_pos_2.convert(32, 0)

    def reset(self):
        obs = super().reset()
        obs = self._process_observations(obs)

        self.player2_reset()
        self.player2_obs = obs[1]
        return obs[0]

    def step(self, action):
        p2_action = self.player2_step(self.player2_obs)
        actions = [action, p2_action]
        obs, reward, done, info = super().step(actions)
        obs = self._process_observations(obs)

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

    def _process_observations(self, obs):
        """Turn rgb images into grayscale and add players positions as white squares"""

        scale_x = GameConfig.screen_x / self.screen_size[0]
        scale_y = GameConfig.screen_y / self.screen_size[1]

        # TODO: Aspect ratio
        wh = math.ceil(Player.players[0].radius / scale_x)
        rect = (wh*2, wh*2)

        # Position for the white rectangle. wh is needed to center it.
        pos_1 = (math.ceil(Player.players[0].position[0] / scale_x)-wh, math.ceil(Player.players[0].position[1] / scale_y)-wh)
        pos_2 = (math.ceil(Player.players[1].position[0] / scale_x)-wh, math.ceil(Player.players[1].position[1] / scale_y)-wh)

        self.screen_player_pos_1.fill((0, 0, 0))
        pygame.draw.rect(self.screen_player_pos_1, (255, 255, 255), (pos_1, rect))

        self.screen_player_pos_2.fill((0, 0, 0))
        pygame.draw.rect(self.screen_player_pos_2, (255, 255, 255), (pos_2, rect))

        # Create observation
        obs = np.dot(obs[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        pos_arr_1 = pygame.surfarray.array3d(self.screen_player_pos_1).swapaxes(0, 1)
        pos_arr_1 = np.dot(pos_arr_1[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        pos_arr_2 = pygame.surfarray.array3d(self.screen_player_pos_2).swapaxes(0, 1)
        pos_arr_2 = np.dot(pos_arr_2[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)

        obs = np.array([np.dstack((obs[0], pos_arr_1)), np.dstack((obs[1], pos_arr_2))])

        return obs
