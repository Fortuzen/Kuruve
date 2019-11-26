import random
import math
import copy

import pygame
from pygame import gfxdraw

from Event import EventManager
from Player import Player
from GameState import GameState
from GameConfig import GameConfig

""" Power ups

Green:
    Speed S
    Slow L
    God G
    Thin T
Red:
    Speed S
    Slow L
    Thick B
    90Turn T
Blue:
    Eraser R

"""


class Powerup:

    font = None  # Init this before __init__
    powerups = []

    def __init__(self, x, y, color, name):
        self.position = [x, y]
        self.radius = 28
        self.color = color
        self.name = name
        self.powerup_text = Powerup.font.render(self.name, True, (255, 255, 255), self.color)
        #self.duration = duration

    # Override this
    def render(self, screen_surface):
        pos = (math.ceil(self.position[0]), math.ceil(self.position[1]))
        pygame.gfxdraw.aacircle(screen_surface, pos[0], pos[1], self.radius, self.color)
        pygame.gfxdraw.filled_circle(screen_surface, pos[0], pos[1], self.radius, self.color)

        powerup_rect = self.powerup_text.get_rect()
        powerup_rect.center = (pos[0], pos[1])
        screen_surface.blit(self.powerup_text, powerup_rect)

    def check_collision(self, player):
        distance = math.sqrt(
            (self.position[0] - player.position[0]) ** 2 +
            (self.position[1] - player.position[1]) ** 2
        )

        if distance <= self.radius:
            return True
        return False

    def handle_collision(self, player):
        pass


""" Green Powerups"""


class PowerupGreenSpeed(Powerup):
    def handle_collision(self, player):
        EventManager.fire_event_after_delay(0, Player.set_speedmodifier_s, player, 2)
        EventManager.fire_event_after_delay(60*3, Player.set_speedmodifier_s, player, 1)


class PowerupGreenSlow(Powerup):
    def handle_collision(self, player):
        EventManager.fire_event_after_delay(0, Player.set_speedmodifier_s, player, 0.5)
        EventManager.fire_event_after_delay(60*3, Player.set_speedmodifier_s, player, 1)


class PowerupGreenGodMode(Powerup):
    def handle_collision(self, player):
        EventManager.fire_event_after_delay(0, Player.set_godmode, player, True)
        EventManager.fire_event_after_delay(60*4, Player.set_godmode, player, False)


class PowerupGreenThin(Powerup):
    def handle_collision(self, player):
        ograd = player.radius
        EventManager.fire_event_after_delay(0, Player.set_thin, player, round(ograd/2))
        EventManager.fire_event_after_delay(60*3, Player.set_thin, player, ograd)


""" Red Powerups"""


class PowerupRedSpeed(Powerup):
    def handle_collision(self, player):
        EventManager.fire_event_after_delay(0, Player.set_speedmodifier_enemies_s, player, 2)
        EventManager.fire_event_after_delay(60*3, Player.set_speedmodifier_enemies_s, player, 1)


class PowerupRedSlow(Powerup):
    def handle_collision(self, player):
        EventManager.fire_event_after_delay(0, Player.set_speedmodifier_enemies_s, player, 0.5)
        EventManager.fire_event_after_delay(60*3, Player.set_speedmodifier_enemies_s, player, 1)


class PowerupRedThick(Powerup):
    def handle_collision(self, player):
        EventManager.fire_event_after_delay(0, Player.set_enemies_thick, player, 6)
        EventManager.fire_event_after_delay(60*3, Player.set_enemies_thick, player, 4)


class PowerupRedTurn90(Powerup):
    def handle_collision(self, player):
        EventManager.fire_event_after_delay(0, Player.set_90_turn_enemies, player, True, 90)
        EventManager.fire_event_after_delay(60*3, Player.set_90_turn_enemies, player, False, 4)


""" Blue Powerups"""


class PowerupBlueEraser(Powerup):
    def handle_collision(self, player):
        EventManager.fire_event_after_delay(0, GameState.clear_screen, GameState.collision_surface)


class PowerupSpawner:
    max_powerup_count = 6
    random_range = (2, 3)
    available_powerups = []

    @staticmethod
    # Add available powerups here
    def init():
        PowerupSpawner.available_powerups.append(PowerupGreenSpeed(0, 0, (0, 255, 0), "S"))

        PowerupSpawner.available_powerups.append(PowerupRedSpeed(0, 0, (255, 0, 0), "S"))

        PowerupSpawner.available_powerups.append(PowerupBlueEraser(0, 0, (0, 0, 255), "R"))

    @staticmethod
    def create_spawn_powerup_event():
        random_time = random.randrange(PowerupSpawner.random_range[0], PowerupSpawner.random_range[1]) * 60
        if len(Powerup.powerups) < PowerupSpawner.max_powerup_count:
            EventManager.fire_event_after_delay(random_time, PowerupSpawner.spawn_powerup)

        EventManager.fire_event_after_delay(random_time, PowerupSpawner.create_spawn_powerup_event)

    @staticmethod
    def spawn_powerup():
        pu_index = random.randrange(0, len(PowerupSpawner.available_powerups))
        pu = copy.copy(PowerupSpawner.available_powerups[pu_index])
        rx = random.randrange(0, GameConfig.screen_x)
        ry = random.randrange(0, GameConfig.screen_y)
        pu.position = [rx, ry]
        Powerup.powerups.append(pu)
        print("Spawn")
