# Kuruve by Fortuzen
# Curve fever clone

import pygame
from pygame import gfxdraw
import math
import collections
import random


""" Game singleton class """


class Game:
    screen_x = 640
    screen_y = 640
    running = True
    screen = None
    collision_surface = None
    framerate = 60
    total_ticks = 0
    avg_fps = 0
    fpsQueue = collections.deque(maxlen=100)

    players = []
    powerups = []

    # as in frames
    wormhole_timer_range = (60, 120)

    @staticmethod
    def update_fps_counter():
        fps = 0
        for v in list(Game.fpsQueue):
            fps += v
        fps = fps / Game.fpsQueue.maxlen
        Game.avg_fps = fps

    @staticmethod
    def reset_game():
        Game.screen.fill((0, 0, 0, 255))
        Game.collision_surface.fill((0, 0, 0, 255))
        print("Player Stats")
        for player in Game.players:
            player.position[0] = random.randint(50, 500)
            player.position[1] = random.randint(50, 500)
            player.angle = 0
            player.alive = True
            print(player.name, ": ", player.score)

    @staticmethod
    def add_score_alive_players():
        for player in Game.players:
            if player.alive:
                player.score += 1


class Player:
    def __init__(self, x, y, a, color, name, keys):
        self.position = [x, y]
        self.angle = a
        self.speed = 2.0
        self.speedModifier = 1.0
        self.turnAmount = 4.0
        self.pixel_collider = None  # Position where the collision is tested
        self.color = color
        self.name = name
        self.alive = True
        self.score = 0
        self.keys = keys  # keys[0] left, keys[1] right
        self.wormhole_timer = random.randint(Game.wormhole_timer_range[0], Game.wormhole_timer_range[1])
        # give this in negative value
        self.wormhole_timer_reset_time = -30

    def input(self, keys):
        if keys[self.keys[0]]:
            self.angle += self.turnAmount
        if keys[self.keys[1]]:
            self.angle -= self.turnAmount

    def update(self):
        dir_x = math.cos(self.angle / 180 * math.pi)
        dir_y = math.sin(self.angle / 180 * math.pi)
        self.position[0] = (self.position[0] + dir_x * self.speed * self.speedModifier) % Game.screen_x
        self.position[1] = (self.position[1] - dir_y * self.speed * self.speedModifier) % Game.screen_y

        pos_x = math.ceil(self.position[0] + dir_x * 4) % Game.screen_x
        pos_y = math.ceil(self.position[1] - dir_y * 4) % Game.screen_y

        self.pixel_collider = (pos_x, pos_y)
        # print(self.pixel_collider)

        self.wormhole_timer -= 1
        if self.wormhole_timer <= self.wormhole_timer_reset_time:
            self.wormhole_timer = random.randint(Game.wormhole_timer_range[0], Game.wormhole_timer_range[1])

    def render(self, screen_surface, collision_surface):
        pos = (math.ceil(self.position[0]), math.ceil(self.position[1]))
        if self.wormhole_timer >= 0:

            pygame.gfxdraw.aacircle(collision_surface, pos[0], pos[1], 4, self.color)
            pygame.gfxdraw.filled_circle(collision_surface, pos[0], pos[1], 4, self.color)

    def render_yellow_dot(self, screen_surface):
        pos = (math.ceil(self.position[0]), math.ceil(self.position[1]))
        pygame.gfxdraw.aacircle(screen_surface, pos[0], pos[1], 3, (255, 255, 0))
        pygame.gfxdraw.filled_circle(screen_surface, pos[0], pos[1], 3, (255, 255, 0))

    @staticmethod
    def clamp(v, minv, maxv):
        return max(minv, min(v, maxv))


class Powerup:
    font = None

    def __init__(self, x, y):
        self.position = [x, y]
        self.radius = 28
        self.color = (0, 255, 0, 255)

    def render(self, screen_surface):
        pos = (math.ceil(self.position[0]), math.ceil(self.position[1]))
        pygame.gfxdraw.aacircle(screen_surface, pos[0], pos[1], self.radius, self.color)
        pygame.gfxdraw.filled_circle(screen_surface, pos[0], pos[1], self.radius, self.color)

        powerup_text = Powerup.font.render("S", True, (255, 255, 255), (0, 255, 0))
        powerup_rect = powerup_text.get_rect()
        powerup_rect.center = (pos[0], pos[1])
        screen_surface.blit(powerup_text, powerup_rect)


def init():
    pygame.init()
    Game.screen = pygame.display.set_mode((Game.screen_x, Game.screen_y))
    Powerup.font = pygame.font.SysFont("comicsansms", 36)
    pygame.font.init()


def mainloop():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)

    # actual game screen
    Game.collision_surface = pygame.Surface((640, 640))

    player1 = Player(50, 50, 0, (255, 0, 0, 255), "Kurve_1", [pygame.K_LEFT, pygame.K_RIGHT])
    player1.speedModifier = 2.0
    player2 = Player(500, 500, 180, (0, 255, 0, 255), "Kurve_2", [pygame.K_a, pygame.K_d])

    Game.players.append(player1)
    Game.players.append(player2)

    player3 = Player(200, 200, 0, (0, 0, 255, 255), "Kurve_3", [pygame.K_n, pygame.K_m])
    Game.players.append(player3)

    # powerup test
    power = Powerup(300, 300)
    Game.powerups.append(power)

    while Game.running:
        # input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game.running = False

        keys = pygame.key.get_pressed()
        # input
        for player in Game.players:
            player.input(keys)

        # logic
        for player in Game.players:
            if not player.alive:
                continue

            player.update()
            # collision
            current_screen = Game.collision_surface.get_at(player.pixel_collider)
            if current_screen != (0, 0, 0, 255) and player.wormhole_timer >= 0:
                print(player.name, " Lost!")
                player.alive = False
                Game.add_score_alive_players()

        # Check alive players
        c = len(Game.players)
        for player in Game.players:
            if not player.alive:
                c -= 1
        # If one player alive, reset the game
        if c <= 1:
            Game.reset_game()

        # render

        for player in Game.players:
            player.render(Game.screen, Game.collision_surface)

        Game.screen.blit(Game.collision_surface, (0, 0))

        for player in Game.players:
            player.render_yellow_dot(Game.screen)

        for powerup in Game.powerups:
            powerup.render(Game.screen)

        # render text
        #fps_text = font.render(str(round(Game.avg_fps)), False, (255, 255, 255), (0, 0, 0, 255))
        #fps_rect = fps_text.get_rect()
        #fps_rect.center = (500, 500)
        #Game.screen.blit(fps_text, fps_rect)

        pygame.display.update()

        # lock fps
        clock.tick(Game.framerate)

        if len(Game.fpsQueue) == Game.fpsQueue.maxlen:
            Game.fpsQueue.popleft()
        Game.fpsQueue.append(clock.get_fps())

        Game.update_fps_counter()
        Game.total_ticks += 1


def main():
    init()
    mainloop()
    pygame.display.quit()


if __name__ == "__main__":
    main()
