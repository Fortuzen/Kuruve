import gym
from gym import spaces

import numpy as np

from kuruve.KurveGame import *

import os

# no input, left, right
possible_actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


# For 2 players, for now
# TODO: Add support for more players
class KuruveGymEnv(gym.Env):
    """
    Gym compatible learning environment for 2 players (for now). Use this as a base for environments.

    :param headless: Show window
    :param observation_size: The game screen will be scales to this size
    :param fps_cap: Limit framerate. 0 is unlimited. 60 is for human play.
    :param frameskip: Skip frames. Previous action will be repeated for the skip duration. Use 1 for no skip (Default).
    :param enable_powerups: Enable powerup spawning.
    :param verbose: Print additional information.
    """

    def __init__(self, headless=False, observation_size=(64, 64), fps_cap=0, frameskip=1, enable_powerups=False,
                 verbose=0):
        print("KuruveGymEnv init")

        self.screen_size = observation_size
        self.frameskip = frameskip
        self.verbose = verbose

        GameConfig.headless = headless
        GameConfig.framerate = fps_cap
        GameConfig.powerups_enabled = enable_powerups
        Game.is_learning_env = True

        Game.init()

        Game.add_player("Kurve_1", GameConfig.default_colors[0], GameConfig.default_controls[0])
        Game.add_player("Kurve_2", GameConfig.default_colors[1], GameConfig.default_controls[1])

        Game.reset_game()

        self.screen_game = pygame.Surface(self.screen_size)
        self.screen_game = self.screen_game.convert(32, 0)

        self.score_difference = 0
        self.total_round_reward = 0

        # For 2 players, rgb image
        self.action_space = spaces.MultiDiscrete([3, 3])
        self.observation_space = spaces.Box(low=0, high=255, dtype=np.uint8,
                                            shape=(2, self.screen_size[1], self.screen_size[0], 3))

    def step(self, action):
        """ """

        actions = [possible_actions[action[0]], possible_actions[action[1]]]
        # Frameskipping
        for _ in range(self.frameskip):

            # Avoid freezing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.running = False
                    exit()

            keys = []
            keys.extend(pygame.key.get_pressed())  # Is this fast?
            for i, act in enumerate(actions):
                player = Player.players[i]
                if act[1]:
                    keys[player.keys[0]] = True
                elif act[2]:
                    keys[player.keys[1]] = True
                player.input(keys)

            Game.game_logic()
            Game.game_render()

            if Game.reseting:
                break

        obs = self._create_observation()

        # Rewards for players
        reward = [0, 0]
        terminal = Game.reseting
        if terminal and Player.players[0].alive:
            reward = [1, -1]
        elif terminal and not Player.players[0].alive:
            reward = [-1, 1]
        self.total_round_reward += reward[0]
        return obs, reward, terminal, None

    def reset(self):
        """ """

        #print("KuruveGymEnv reset")
        self.score_difference = Player.players[0].score - Player.players[1].score
        pid = os.getpid()
        if self.verbose:
            print("PID", pid, "Score Difference", self.score_difference)
            print(self.total_round_reward)
        self.total_round_reward = 0
        #print("PID", pid, "Total reward", self.total_reward)

        if not Game.reseting:
            Game.reset_game()

        # Process one tick to reset the game
        Game.game_logic()
        Game.game_render()

        obs = self._create_observation()

        return obs

    def render(self, mode="human"):
        """ """

        raise NotImplementedError

    def close(self):
        """ """

        Game.close()
        print("Game closed")

    def seed(self, seed=None):
        """ """

        raise NotImplementedError

    def _grayscale(self, img):
        arr = pygame.surfarray.array3d(img)
        arr = arr.dot([0.298, 0.587, 0.114])[:, :, None].repeat(3, axis=2);
        return pygame.surfarray.make_surface(arr)

    def _create_observation(self):
        #pygame.transform.scale(GameState.screen, self.screen_size, self.small_screen)

        pygame.transform.smoothscale(GameState.screen, self.screen_size, self.screen_game)
        p2_surface = self.screen_game.copy()

        # Swap axis because otherwise image's orientation is wrong.
        obs = np.array([pygame.surfarray.array3d(self.screen_game).swapaxes(0, 1),
                        pygame.surfarray.array3d(p2_surface).swapaxes(0, 1)])

        return obs
