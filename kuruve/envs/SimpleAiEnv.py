from kuruve.envs.GymEnv import KuruveGymEnv
from kuruve.KurveGame import *
from gym import spaces
import pygame
import numpy as np
import math


class SimpleAiEnv(KuruveGymEnv):
    """
    Environment with an AI opponent
    """

    def __init__(self, headless=False, observation_size=(64, 64), fps_cap=0, frameskip=0, enable_powerups=False,
                 verbose=0, ai_count=1):

        super().__init__(headless, observation_size, fps_cap, frameskip, enable_powerups, verbose, 1)

        self.ai_count = ai_count
        for i in range(1, self.ai_count+1):
            Game.add_player("Kurve_"+str(i+1), GameConfig.default_colors[i], GameConfig.default_controls[i], is_ai=True)
            self.player_count += 1

        self.screen_player_pos_1 = pygame.Surface(self.screen_size)
        self.screen_player_pos_1 = self.screen_player_pos_1.convert(32, 0)

        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=0, high=255, dtype=np.uint8,
                                            shape=(self.screen_size[1], self.screen_size[0], 2))

        Game.reset_game()

    def reset(self):
        obs = super().reset()
        return self._process_observation(obs)

    def step(self, action):
        actions = [0, 0]
        actions[0] = action
        obs, reward, done, info = super().step(actions)
        obs = self._process_observation(obs)
        reward = reward[0]
        info = {}
        return obs, reward, done, info

    def render(self, mode="human"):
        raise NotImplementedError

    def close(self):
        super().close()
        print("Game closed")

    def seed(self, seed=None):
        raise NotImplementedError

    def _process_observation(self, obs):
        """Turn rgb image into grayscale and add players positions as white squares"""

        scale_x = GameConfig.screen_x / self.screen_size[0]
        scale_y = GameConfig.screen_y / self.screen_size[1]

        # TODO: Aspect ratio
        wh = math.ceil(Player.players[0].radius / scale_x)
        rect = (wh*2, wh*2)

        # Position for the white rectangle. wh is needed to center it.
        pos_1 = (math.ceil(Player.players[0].position[0] / scale_x)-wh, math.ceil(Player.players[0].position[1] / scale_y)-wh)

        self.screen_player_pos_1.fill((0, 0, 0))
        pygame.draw.rect(self.screen_player_pos_1, (255, 255, 255), (pos_1, rect))

        # Create observation
        obs = np.dot(obs[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        pos_arr_1 = pygame.surfarray.pixels3d(self.screen_player_pos_1).swapaxes(0, 1)
        pos_arr_1 = pos_arr_1[..., 1].astype(np.uint8)

        obs = np.dstack((obs, pos_arr_1))

        return obs
