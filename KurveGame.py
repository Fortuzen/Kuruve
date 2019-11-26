import pygame
from pygame import gfxdraw
import math
import collections
import random

from Powerup import PowerupSpawner, Powerup
from Event import EventManager
from Player import Player

from GameState import GameState
from GameConfig import GameConfig

""" Game singleton class """


class Game:

    avg_fps = 0
    fpsQueue = collections.deque(maxlen=100)

    # learning env
    is_learning_env = False
    reseting = True

    @staticmethod
    def update_fps_counter():
        fps = 0
        for v in list(Game.fpsQueue):
            fps += v
        fps = fps / Game.fpsQueue.maxlen
        Game.avg_fps = fps
        pygame.display.set_caption(str(fps))

    @staticmethod
    def reset_game():
        GameState.screen.fill((0, 0, 0, 255))
        GameState.collision_surface.fill((0, 0, 0, 255))
        # Reset players
        print("Player Stats")
        for player in Player.players:
            player.position[0] = random.randint(50, 500)
            player.position[1] = random.randint(50, 500)
            player.angle = random.randint(0, 360)
            player.alive = True
            player.radius = 4

            player.speedModifier = 1.0
            player.godmode = False
            player.turn90 = False

            print(player.name, ": ", player.score)

        EventManager.events = []

        if GameConfig.powerups_enabled:
            Powerup.powerups = []
            PowerupSpawner.create_spawn_powerup_event()

        Game.reseting = True

    @staticmethod
    def add_score_alive_players():
        for player in Player.players:
            if player.alive:
                player.score += 1

    @staticmethod
    def init():
        pygame.init()
        GameState.screen = pygame.display.set_mode((GameConfig.screen_x, GameConfig.screen_y))
        # Game.screen = pygame.Surface((640, 640)) It is possible headless
        Powerup.font = pygame.font.SysFont("comicsansms", 36)
        pygame.font.init()

        # actual game screen
        GameState.collision_surface = pygame.Surface((GameConfig.screen_x, GameConfig.screen_y))

    @staticmethod
    def game_input():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameState.running = False

        keys = pygame.key.get_pressed()
        for player in Player.players:
            player.input(keys)

    @staticmethod
    def game_logic():
        EventManager.process_events(GameState.total_ticks)  # handle events

        for player in Player.players:
            if not player.alive:
                continue

            player.update()
            # collision
            current_screen = GameState.collision_surface.get_at(player.pixel_collider)
            if current_screen != (0, 0, 0, 255) and player.wormhole_timer >= 0 and not player.godmode:  # make better
                print(player.name, " Lost!")
                player.alive = False
                Game.add_score_alive_players()

            for pu in Powerup.powerups:
                if pu.check_collision(player):
                    pu.handle_collision(player)
                    Powerup.powerups.remove(pu)
                    print("Powerup collision")
                    break

        # Check alive players
        c = len(Player.players)
        for player in Player.players:
            if not player.alive:
                c -= 1
        # If one/zero players alive, reset the game
        if c <= 1:
            Game.reset_game()

    @staticmethod
    def game_render():
        for player in Player.players:
            player.render(GameState.screen, GameState.collision_surface)

        GameState.screen.blit(GameState.collision_surface, (0, 0))

        for player in Player.players:
            player.render_yellow_dot(GameState.screen)

        for powerup in Powerup.powerups:
            powerup.render(GameState.screen)

        pygame.display.update()

    @staticmethod
    def add_player(name, color, controls):
        player = Player(0, 0, 0, color, name, controls)
        Player.players.append(player)
