import pygame
import numpy as np

from kuruve.KurveGame import *
from kuruve.envs.GymEnv import KuruveGymEnv
from gym import spaces

class RandomEnv(KuruveGymEnv):
    """
    Environment in which the second worm's actions are random. Not very useful for training because
    the random worm does not survive for long.
    """

    def __init__(self, headless=False, observation_size=(64, 64), fps_cap=0, frameskip=0, enable_powerups=False,
                 verbose=0):
        super().__init__(headless, observation_size, fps_cap, frameskip, enable_powerups, verbose)

        self.screen_player_pos = pygame.Surface(self.screen_size)
        self.screen_player_pos = self.screen_player_pos.convert(32, 0)

        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=0, high=255, dtype=np.uint8,
                                            shape=(self.screen_size[0], self.screen_size[1], 2))

    def reset(self):
        obs = super().reset()
        return obs[0]

    def step(self, action):
        actions = [action, self.action_space.sample()]
        obs, reward, done, info = super().step(actions)
        obs = self._process_observation(obs)
        reward = reward[0]
        #info = {"total_reward": self.total_reward, "score_difference": self.score_difference}
        info = {}
        return obs[0], reward, done, info

    def render(self, mode="human"):
        raise NotImplementedError

    def close(self):
        super().close()
        print("Game closed")

    def seed(self, seed=None):
        raise NotImplementedError

    def _process_observation(self, obs):

        scale_x = GameConfig.screen_x / self.screen_size[0]
        scale_y = GameConfig.screen_y / self.screen_size[1]
        wh = math.ceil(Player.players[0].radius / scale_x)
        rect = (wh * 2, wh * 2)
        pos_1 = (math.ceil(Player.players[0].position[0] / scale_x) - wh,
                 math.ceil(Player.players[0].position[1] / scale_y) - wh)

        pygame.transform.smoothscale(GameState.screen, self.screen_size, self.screen_game)

        # Draw square at player's position
        self.screen_player_pos.fill((0, 0, 0))
        pygame.draw.rect(self.screen_player_pos, (255, 255, 255), (pos_1, rect))

        obs = pygame.surfarray.array3d(self.screen_game).swapaxes(0, 1)
        obs = np.dot(obs[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)

        pos_arr = pygame.surfarray.array3d(self.screen_player_pos).swapaxes(0, 1)
        pos_arr = np.dot(pos_arr[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)

        obs = np.dstack((obs, pos_arr))

        return obs
