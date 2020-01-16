import gym
from gym import spaces

import numpy as np

from KurveGame import *
from GameConfig import GameConfig
from Powerup import PowerupSpawner

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
    :param frameskip: Skip frames. Previous action will be repeated for the skip duration. Use 1 for no skip.
    :param enable_powerups: Enable powerup spawning.
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

        # For 2 players
        self.action_space = spaces.MultiDiscrete([3, 3])
        self.observation_space = spaces.Box(low=0, high=255, dtype=np.uint8,
                                            shape=(2, self.screen_size[1], self.screen_size[0], 3))

    def step(self, action):
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
        raise NotImplementedError

    def close(self):
        Game.close()
        print("Game closed")

    def seed(self, seed=None):
        raise NotImplementedError

    def _grayscale(self, img):
        arr = pygame.surfarray.array3d(img)
        arr = arr.dot([0.298, 0.587, 0.114])[:, :, None].repeat(3, axis=2);
        return pygame.surfarray.make_surface(arr)

    def _all2white(self, img):
        arr = pygame.surfarray.array3d(img)
        arr[np.any(arr != [0, 0, 0], axis=-1)] = [255, 255, 255]

        return pygame.surfarray.make_surface(arr)

    def _create_observation(self):
        #pygame.transform.scale(GameState.screen, self.screen_size, self.small_screen)
        pygame.transform.smoothscale(GameState.screen, self.screen_size, self.screen_game)
        #self.small_screen = self._grayscale(self.small_screen)
        #self.small_screen = self._all2white(self.small_screen)
        p2_surface = self.screen_game.copy()

        scale_x = GameConfig.screen_x / self.screen_size[0]
        scale_y = GameConfig.screen_y / self.screen_size[1]
        # TODO: Remove hardcoding
        pos_1 = (math.ceil(Player.players[0].position[0] / scale_x)-1, math.ceil(Player.players[0].position[1] / scale_y)-1)
        pos_2 = (math.ceil(Player.players[1].position[0] / scale_x)-1, math.ceil(Player.players[1].position[1] / scale_y)-1)
        # TODO: What if obs size ratio not 1:1
        radius = math.ceil(Player.players[0].radius / scale_x)

        # Draw red dots at players' positions
        #pygame.draw.circle(self.small_screen, (255, 0, 0), pos_1, radius)
        #pygame.draw.circle(p2_surface, (255, 0, 0), pos_2, radius)
        pygame.draw.rect(self.small_screen, (255, 255, 255), (pos_1, (2, 2)))
        pygame.draw.rect(p2_surface, (255, 255, 255), (pos_2, (2, 2)))

        #obs = np.array([pygame.surfarray.array3d(self.small_screen).swapaxes(0, 1), None])
        obs = np.array([pygame.surfarray.array3d(self.small_screen).swapaxes(0, 1),
                        pygame.surfarray.array3d(p2_surface).swapaxes(0, 1)])

        return obs
