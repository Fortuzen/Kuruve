import random
import math

import pygame
from pygame import gfxdraw

from .Event import EventManager
from .GameState import GameState
from .GameConfig import GameConfig


class Player:
    """
    Player class
    :param x: Starting position x
    :param y: Starting position y
    :param a: Starting angle
    :param color: Player's color
    :param name: Player's name
    :param keys: Player's controls
    """

    players = []

    def __init__(self, x, y, a, color, name, keys, is_ai=False):
        self.position = [x, y]
        self.previous_position = [x, y]
        self.radius = 3
        self.angle = a
        self.speed = 1.5

        self.turnAmount = 4.0
        self.pixel_collider = None  # Position where the collision is tested
        self.color = color
        self.name = name
        self.alive = True
        self.score = 0
        self.keys = keys  # keys[0] left, keys[1] right
        self.wormhole_timer = random.randint(GameConfig.wormhole_timer_range[0], GameConfig.wormhole_timer_range[1])
        # give this in negative value, duration of the wormhole
        self.wormhole_timer_reset_time = -20

        # Powerup related
        self.godmode = False
        self.speedModifier = 1.0
        self.turn90 = False
        self.turn90previousKey = None

        # Simple AI
        self.is_ai = is_ai
        self.ai_area = 32
        self.left_area = pygame.Surface((self.ai_area, self.ai_area)).convert(32, 0)
        self.top_area = pygame.Surface((self.ai_area, self.ai_area)).convert(32, 0)
        self.right_area = pygame.Surface((self.ai_area, self.ai_area)).convert(self.ai_area, 0)

    def input(self, keys):
        if self.is_ai:
            keys = self.ai_decision(keys)
        # left
        ogangle = self.angle
        if keys[self.keys[0]]:
            self.angle += self.turnAmount
        # right
        if keys[self.keys[1]]:
            self.angle -= self.turnAmount

        self.handle_90turn(keys, ogangle)

    def update(self):
        # store previous position
        self.previous_position[0] = self.position[0]
        self.previous_position[1] = self.position[1]
        # Move
        dir_x = math.cos(self.angle / 180 * math.pi)
        dir_y = math.sin(self.angle / 180 * math.pi)
        self.position[0] = (self.position[0] + dir_x * self.speed * self.speedModifier) % GameConfig.screen_x
        self.position[1] = (self.position[1] - dir_y * self.speed * self.speedModifier) % GameConfig.screen_y

        # Position for collision check, add 1 to radius because slow pu fails otherwise
        pos_x = math.ceil(self.position[0] + dir_x * (self.radius+1)) % GameConfig.screen_x
        pos_y = math.ceil(self.position[1] - dir_y * (self.radius+1)) % GameConfig.screen_y
        # Set collision check position
        self.pixel_collider = (pos_x, pos_y)

        self.wormhole_timer -= 1
        if self.wormhole_timer <= self.wormhole_timer_reset_time:
            self.wormhole_timer = random.randint(GameConfig.wormhole_timer_range[0], GameConfig.wormhole_timer_range[1])

    def render(self, screen_surface, collision_surface):
        pos = (math.ceil(self.position[0]), math.ceil(self.position[1]))
        if self.wormhole_timer >= 0 and not self.godmode:
            # Collision surface
            pygame.gfxdraw.aacircle(collision_surface, pos[0], pos[1], self.radius, self.color)
            pygame.gfxdraw.filled_circle(collision_surface, pos[0], pos[1], self.radius, self.color)
            # Screen surface
            pygame.gfxdraw.aacircle(screen_surface, pos[0], pos[1], self.radius, self.color)
            pygame.gfxdraw.filled_circle(screen_surface, pos[0], pos[1], self.radius, self.color)

    def render_yellow_dot(self, screen_surface):
        pos = (math.ceil(self.position[0]), math.ceil(self.position[1]))
        prev_pos = (math.ceil(self.previous_position[0]), math.ceil(self.previous_position[1]))

        # Previous position, removes yellow dot
        if self.wormhole_timer >= 0 and not self.godmode:
            pygame.gfxdraw.aacircle(screen_surface, prev_pos[0], prev_pos[1], self.radius, self.color)
            pygame.gfxdraw.filled_circle(screen_surface, prev_pos[0], prev_pos[1], self.radius, self.color)
        else:
            # Old solution:
            # Looks "bad" but it is a necessary sacrifice
            #pygame.gfxdraw.filled_circle(screen_surface, prev_pos[0], prev_pos[1], self.radius+1, (0, 0, 0))
            # New solution.
            area = (prev_pos[0]-self.radius, prev_pos[1]-self.radius, self.radius * 2, self.radius * 2)
            screen_surface.blit(GameState.collision_surface, (area[0], area[1]), area)

        # Current position, draw yellow dot
        pygame.gfxdraw.aacircle(screen_surface, pos[0], pos[1], self.radius-1, (255, 255, 0))
        pygame.gfxdraw.filled_circle(screen_surface, pos[0], pos[1], self.radius-1, (255, 255, 0))

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

    def ai_decision(self, keys):
        """Very simple ai. Slightly better than random"""

        keys_temp = []
        keys_temp.extend(keys)
        # Fill areas
        r = 32
        r2 = self.ai_area/2
        rad_left = (self.angle + 90) / 180 * math.pi
        rad_right = (self.angle - 90) / 180 * math.pi
        rad_top = self.angle / 180 * math.pi

        rect_area_left = (self.position[0] + r*math.cos(rad_left) - r2, self.position[1] - r*math.sin(rad_left) - r2, self.ai_area, self.ai_area)
        rect_area_right = (self.position[0] + r * math.cos(rad_right) - r2, self.position[1] - r * math.sin(rad_right) - r2, self.ai_area, self.ai_area)
        rect_area_top = (self.position[0] + r * math.cos(rad_top) - r2, self.position[1] - r * math.sin(rad_top) - r2, self.ai_area, self.ai_area)

        self.left_area.blit(GameState.collision_surface, (0, 0),  rect_area_left)
        self.right_area.blit(GameState.collision_surface, (0, 0), rect_area_right)
        self.top_area.blit(GameState.collision_surface, (0, 0), rect_area_top)

        left = sum(pygame.transform.average_color(self.left_area))
        right = sum(pygame.transform.average_color(self.right_area))
        top = sum(pygame.transform.average_color(self.top_area))

        # candidates
        thres = 1
        can_turn = [left < thres, right < thres, top < thres]
        #print(can_turn)
        i = 0
        actions = list()
        for b in can_turn:
            if b:
                if i == 0:
                    actions.append(self.keys[0])
                elif i == 1:
                    actions.append(self.keys[1])
                elif i == 2:
                    actions.append(0)
            i += 1
        if len(actions) == 0:
            actions.extend([self.keys[0], self.keys[1], 0])
        action = random.choice(actions)
        keys_temp[action] = 1

        # Debug stuff
        """
        pygame.draw.rect(GameState.screen, (255, 255, 255), rect_area_left)
        pygame.draw.rect(GameState.screen, (255, 255, 255), rect_area_right)
        pygame.draw.rect(GameState.screen, (255, 255, 255), rect_area_top)
        pygame.display.flip()
        print(self.position[0], self.position[1], rect_area_left)
        print(left, top, right)
        """

        return keys_temp

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
