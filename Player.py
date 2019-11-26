import random
import math

import pygame
from pygame import gfxdraw

from Event import EventManager
from GameState import  GameState
from GameConfig import GameConfig

class Player:
    players = []

    def __init__(self, x, y, a, color, name, keys):
        self.position = [x, y]
        self.radius = 4
        self.angle = a
        self.speed = 2.0

        self.turnAmount = 4.0
        self.pixel_collider = None  # Position where the collision is tested
        self.color = color
        self.name = name
        self.alive = True
        self.score = 0
        self.keys = keys  # keys[0] left, keys[1] right
        self.wormhole_timer = random.randint(GameConfig.wormhole_timer_range[0], GameConfig.wormhole_timer_range[1])
        # give this in negative value
        self.wormhole_timer_reset_time = -30

        # Powerup related
        self.godmode = False
        self.speedModifier = 1.0
        self.turn90 = False
        self.turn90previousKey = None

    def input(self, keys):

        # left
        ogangle = self.angle
        if keys[self.keys[0]]:
            self.angle += self.turnAmount
        # right
        if keys[self.keys[1]]:
            self.angle -= self.turnAmount

        self.handle_90turn(keys, ogangle)

    def update(self):
        dir_x = math.cos(self.angle / 180 * math.pi)
        dir_y = math.sin(self.angle / 180 * math.pi)
        self.position[0] = (self.position[0] + dir_x * self.speed * self.speedModifier) % GameConfig.screen_x
        self.position[1] = (self.position[1] - dir_y * self.speed * self.speedModifier) % GameConfig.screen_y

        # Position for collision check, add 1 to radius because slow pu fails otherwise
        pos_x = math.ceil(self.position[0] + dir_x * (self.radius+1)) % GameConfig.screen_x
        pos_y = math.ceil(self.position[1] - dir_y * (self.radius+1)) % GameConfig.screen_y

        self.pixel_collider = (pos_x, pos_y)
        # print(self.pixel_collider)

        self.wormhole_timer -= 1
        if self.wormhole_timer <= self.wormhole_timer_reset_time:
            self.wormhole_timer = random.randint(GameConfig.wormhole_timer_range[0], GameConfig.wormhole_timer_range[1])

    def render(self, screen_surface, collision_surface):
        pos = (math.ceil(self.position[0]), math.ceil(self.position[1]))
        if self.wormhole_timer >= 0 and not self.godmode:

            pygame.gfxdraw.aacircle(collision_surface, pos[0], pos[1], self.radius, self.color)
            pygame.gfxdraw.filled_circle(collision_surface, pos[0], pos[1], self.radius, self.color)

    def render_yellow_dot(self, screen_surface):
        pos = (math.ceil(self.position[0]), math.ceil(self.position[1]))
        pygame.gfxdraw.aacircle(screen_surface, pos[0], pos[1], self.radius, (255, 255, 0))
        pygame.gfxdraw.filled_circle(screen_surface, pos[0], pos[1], self.radius, (255, 255, 0))

    def handle_90turn(self, keys, og_angle):
        if self.turn90:
            noinput = True
            self.angle = og_angle

            if keys[self.keys[0]]:
                if self.turn90previousKey != self.keys[0]:
                    self.angle += 90
                noinput = False
                self.turn90previousKey = self.keys[0]

            if keys[self.keys[1]]:
                if self.turn90previousKey != self.keys[1]:
                    self.angle -= 90
                noinput = False
                self.turn90previousKey = self.keys[1]

            if noinput:
                self.turn90previousKey = None

    @staticmethod
    def clamp(v, minv, maxv):
        return max(minv, min(v, maxv))

    # Used in event
    def set_speedmodifier(self, val):
        self.speedModifier = val

    @staticmethod
    def set_speedmodifier_s(player, val):
        player.speedModifier = val
        EventManager.fire_event_after_delay(60*3, Player.set_speedmodifier_s, player, 1)

    @staticmethod
    def set_speedmodifier_enemies_s(player, val):
        for p in Player.players:
            if p == player:
                continue
            p.speedModifier = val

    @staticmethod
    def set_godmode(player, val):
        player.godmode = val

    @staticmethod
    def set_thin(player, val):
        player.radius = val

    @staticmethod
    def set_enemies_thick(player, val):
        for p in Player.players:
            if p == player:
                continue
            p.radius = val

    @staticmethod
    def set_90_turn_enemies(player, turn_bool, turn_val):
        for p in Player.players:
            if p == player:
                continue
            p.turn90 = turn_bool
            p.turnAmount = turn_val
