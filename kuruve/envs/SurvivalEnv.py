import gym
from gym import spaces

import numpy as np

from kuruve.KurveGame import *

import os

# no input, left, right
possible_actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]



class SurvivalEnv(gym.Env):
    """
    Gym compatible learning environment. Try survive as long as possible.

    :param headless: Show window
    :param observation_size: The game screen will be scales to this size
    :param fps_cap: Limit framerate. 0 is unlimited. 60 is for human play.
    :param frameskip: Skip frames. Previous action will be repeated for the skip duration. Use 1 for no skip.
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
        GameConfig.survival = True
        Game.is_learning_env = True

        Game.init()

        Game.add_player("Kurve_1", GameConfig.default_colors[0], GameConfig.default_controls[0])

        Game.reset_game()

        # Create small surfaces and convert them to proper format
        self.screen_game = pygame.Surface(self.screen_size)
        self.screen_game = self.screen_game.convert(32, 0)
        self.screen_player_pos = pygame.Surface(self.screen_size)
        self.screen_player_pos = self.screen_player_pos.convert(32, 0)

        self.total_round_reward = 0

        self.action_space = spaces.Discrete(3)
        # TODO: Decide which one is better
        # 1.obs=grayscale image of game, 2.obs= player position
        self.observation_space = spaces.Box(low=0, high=255, dtype=np.uint8, shape=(self.screen_size[1], self.screen_size[0], 2))
        # Original, grayscale image
        #self.observation_space = spaces.Box(low=0, high=255, dtype=np.uint8, shape=(self.screen_size[1], self.screen_size[0], 1))
        self.reward_range = (0, float('inf'))

    def step(self, action):
        actions = [possible_actions[action]]
        reward = 0
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
            reward += 0.001  # Reward for every survived frame
            if Game.reseting:
                break

        obs = self._create_observation()

        # No reward for hitting the wall
        terminal = Game.reseting
        if terminal and Player.players[0].alive:
            reward = 0

        self.total_round_reward += reward

        return obs, reward, terminal, {}

    def reset(self):
        #print("KuruveGymEnv reset")
        pid = os.getpid()
        if self.verbose:
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

    def _create_observation(self):
        #pygame.transform.scale(GameState.screen, self.screen_size, self.small_screen)

        pygame.transform.smoothscale(GameState.screen, self.screen_size, self.screen_game)

        scale_x = GameConfig.screen_x / self.screen_size[0]
        scale_y = GameConfig.screen_y / self.screen_size[1]
        # TODO: Aspect ratio
        wh = math.ceil(Player.players[0].radius / scale_x)
        rect = (wh*2, wh*2)

        # Position for the white rectangle. wh is needed to center it.
        pos_1 = (math.ceil(Player.players[0].position[0] / scale_x)-wh, math.ceil(Player.players[0].position[1] / scale_y)-wh)

        # Draw rect at players' positions
        # TODO: Replace fill with draw. Insted of fill, draw black rect over the white.
        self.screen_player_pos.fill((0, 0, 0))
        pygame.draw.rect(self.screen_player_pos, (255, 255, 255), (pos_1, (2, 2)))

        # Create observation
        obs = pygame.surfarray.array3d(self.screen_game).swapaxes(0, 1)
        obs = np.dot(obs[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)

        pos_arr = pygame.surfarray.array3d(self.screen_player_pos).swapaxes(0, 1)
        pos_arr = np.dot(pos_arr[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        obs = np.dstack((obs, pos_arr))

        return obs
