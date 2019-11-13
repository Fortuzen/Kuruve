# Kuruve by Fortuzen
# Curve fever clone

import pygame
from pygame import gfxdraw
import math
import collections
import random
import copy
import os

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
        Game.screen.fill((0, 0, 0, 255))
        Game.collision_surface.fill((0, 0, 0, 255))
        # Reset players
        print("Player Stats")
        for player in Game.players:
            player.position[0] = random.randint(50, 500)
            player.position[1] = random.randint(50, 500)
            player.angle = 0
            player.alive = True
            player.radius = 4

            player.speedModifier = 1.0
            player.godmode = False
            player.turn90 = False

            print(player.name, ": ", player.score)

        EventManager.events = []
        Game.powerups = []
        PowerupSpawner.create_spawn_powerup_event()

        Game.reseting = True


    @staticmethod
    def add_score_alive_players():
        for player in Game.players:
            if player.alive:
                player.score += 1
    @staticmethod
    def clear_screen(surface):
        surface.fill((0, 0, 0, 255))


class Player:
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
        self.wormhole_timer = random.randint(Game.wormhole_timer_range[0], Game.wormhole_timer_range[1])
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

        if self.turn90:
            noinput = True
            self.angle = ogangle

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

    def update(self):
        dir_x = math.cos(self.angle / 180 * math.pi)
        dir_y = math.sin(self.angle / 180 * math.pi)
        self.position[0] = (self.position[0] + dir_x * self.speed * self.speedModifier) % Game.screen_x
        self.position[1] = (self.position[1] - dir_y * self.speed * self.speedModifier) % Game.screen_y

        # Position for collision check, add 1 to radius because slow pu fails otherwise
        pos_x = math.ceil(self.position[0] + dir_x * (self.radius+1)) % Game.screen_x
        pos_y = math.ceil(self.position[1] - dir_y * (self.radius+1)) % Game.screen_y

        self.pixel_collider = (pos_x, pos_y)
        # print(self.pixel_collider)

        self.wormhole_timer -= 1
        if self.wormhole_timer <= self.wormhole_timer_reset_time:
            self.wormhole_timer = random.randint(Game.wormhole_timer_range[0], Game.wormhole_timer_range[1])

    def render(self, screen_surface, collision_surface):
        pos = (math.ceil(self.position[0]), math.ceil(self.position[1]))
        if self.wormhole_timer >= 0 and not self.godmode:

            pygame.gfxdraw.aacircle(collision_surface, pos[0], pos[1], self.radius, self.color)
            pygame.gfxdraw.filled_circle(collision_surface, pos[0], pos[1], self.radius, self.color)

    def render_yellow_dot(self, screen_surface):
        pos = (math.ceil(self.position[0]), math.ceil(self.position[1]))
        pygame.gfxdraw.aacircle(screen_surface, pos[0], pos[1], self.radius, (255, 255, 0))
        pygame.gfxdraw.filled_circle(screen_surface, pos[0], pos[1], self.radius, (255, 255, 0))

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
        for p in Game.players:
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
        for p in Game.players:
            if p == player:
                continue
            p.radius = val

    @staticmethod
    def set_90_turn_enemies(player, turnBool, turnVal):
        for p in Game.players:
            if p == player:
                continue
            p.turn90 = turnBool
            p.turnAmount = turnVal

# TODO: Refactor render, do not repeat yourself
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
    # Init this before __init__
    font = None

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
        EventManager.fire_event_after_delay(0, Game.clear_screen, Game.collision_surface)


class PowerupSpawner:
    max_powerup_count = 6
    random_range = (2, 3)
    available_powerups = []

    @staticmethod
    # Add available powerups here
    def init():
        PowerupSpawner.available_powerups.append(PowerupGreenSpeed(0, 0, (0, 255, 0), "S"))

        PowerupSpawner.available_powerups.append(PowerupRedSpeed(0, 0, (255, 0, 0), "S"))

    @staticmethod
    def create_spawn_powerup_event():
        random_time = random.randrange(PowerupSpawner.random_range[0], PowerupSpawner.random_range[1]) * 60
        #print(random_time)
        if len(Game.powerups) < PowerupSpawner.max_powerup_count:
            EventManager.fire_event_after_delay(random_time, PowerupSpawner.spawn_powerup)

        EventManager.fire_event_after_delay(random_time, PowerupSpawner.create_spawn_powerup_event)

    @staticmethod
    def spawn_powerup():
        pu_index = random.randrange(0, len(PowerupSpawner.available_powerups))
        pu = copy.copy(PowerupSpawner.available_powerups[pu_index])
        rx = random.randrange(0, Game.screen_x)
        ry = random.randrange(0, Game.screen_y)
        pu.position = [rx, ry]
        Game.powerups.append(pu)
        print("Spawn")

def test(asd):
    print(asd)
    # EventManager.fire_event_after_delay(60 * 2, test)


class Event:
    def __init__(self, tick, function, *args):
        self.trigger = function
        self.args = args
        self.tick = tick


class EventManager:
    events = []

    @staticmethod
    def process_events():
        for event in EventManager.events:
            if event.tick <= Game.total_ticks:
                # print("asd", event.trigger)
                # print("asd", event.tick)
                event.trigger(*event.args)
                EventManager.events.remove(event) # hmmm


    @staticmethod
    def fire_event_after_delay(ticks, function, *args):
        # print(args)
        e = Event(ticks + Game.total_ticks, function, *args)
        EventManager.events.append(e)


def init():
    pygame.init()
    Game.screen = pygame.display.set_mode((Game.screen_x, Game.screen_y))
    #Game.screen = pygame.Surface((640, 640)) It is possible headless
    Powerup.font = pygame.font.SysFont("comicsansms", 36)
    pygame.font.init()

    # actual game screen
    Game.collision_surface = pygame.Surface((640, 640))

#TODO: Change name
def input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Game.running = False

    keys = pygame.key.get_pressed()
    for player in Game.players:
        player.input(keys)


def logic():
    EventManager.process_events()  # handle events

    for player in Game.players:
        if not player.alive:
            continue

        player.update()
        # collision
        current_screen = Game.collision_surface.get_at(player.pixel_collider)
        if current_screen != (0, 0, 0, 255) and player.wormhole_timer >= 0 and not player.godmode:  # make better
            print(player.name, " Lost!")
            player.alive = False
            Game.add_score_alive_players()

        for pu in Game.powerups:
            if pu.check_collision(player):
                pu.handle_collision(player)
                Game.powerups.remove(pu)
                print("Powerup collision")
                break

    # Check alive players
    c = len(Game.players)
    for player in Game.players:
        if not player.alive:
            c -= 1
    # If one/zero players alive, reset the game
    if c <= 1:
        Game.reset_game()



def render():
    for player in Game.players:
        player.render(Game.screen, Game.collision_surface)

    Game.screen.blit(Game.collision_surface, (0, 0))

    for player in Game.players:
        player.render_yellow_dot(Game.screen)

    for powerup in Game.powerups:
        powerup.render(Game.screen)

    # render text
    # fps_text = font.render(str(round(Game.avg_fps)), False, (255, 255, 255), (0, 0, 0, 255))
    # fps_rect = fps_text.get_rect()
    # fps_rect.center = (500, 500)
    # Game.screen.blit(fps_text, fps_rect)

    pygame.display.update()

def mainloop():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)

    player1 = Player(50, 50, 0, (255, 0, 0, 255), "Kurve_1", [pygame.K_LEFT, pygame.K_RIGHT])
    player1.speedModifier = 1
    player2 = Player(500, 500, 180, (0, 255, 0, 255), "Kurve_2", [pygame.K_a, pygame.K_d])

    Game.players.append(player1)
    Game.players.append(player2)

    player3 = Player(200, 200, 0, (0, 0, 255, 255), "Kurve_3", [pygame.K_n, pygame.K_m])
    Game.players.append(player3)

    # powerup test
    #power1 = PowerupGreenSpeed(300, 300, (0, 255, 0), "S")
    #power1 = PowerupGreenGodMode(300, 300)
    #power1 = PowerupGreenSlow(300, 300)
    #power1 = PowerupRedSlow(300, 300)
    #power1 = PowerupGreenThin(300, 300)
    #power1 = PowerupRedThick(300, 300)
    #power1 = PowerupRedTurn90(300, 300, (255, 0, 0), "T")
    #Game.powerups.append(power1)

    #power2 = PowerupRedSpeed(300, 500)
    #Game.powerups.append(power2)

    #power3 = PowerupBlueEraser(100, 100)
    #Game.powerups.append(power3)

    # Starts powerup spawning
    PowerupSpawner.init()
    PowerupSpawner.create_spawn_powerup_event()

    while Game.running:
        input()
        logic()
        render()

        # lock fps
        clock.tick(Game.framerate)

        if len(Game.fpsQueue) == Game.fpsQueue.maxlen:
            Game.fpsQueue.popleft()
        Game.fpsQueue.append(clock.get_fps())

        Game.update_fps_counter()
        Game.total_ticks += 1

# When run directly
def main():
    init()
    mainloop()
    pygame.display.quit()


if __name__ == "__main__":
    main()

# For learning environment
# Prototype 2 player


def make():
    # Hide window, not ready
    #os.putenv('SDL_VIDEODRIVER', 'fbcon')
    #os.environ["SDL_VIDEODRIVER"] = "dummy"

    init()
    Game.framerate = 0
    Game.is_learning_env = True

    player1 = Player(50, 50, 0, (255, 0, 0), "Kurve_1", [pygame.K_LEFT, pygame.K_RIGHT])
    player2 = Player(500, 500, 180, (0, 255, 0), "Kurve_2", [pygame.K_a, pygame.K_d])
    Game.players.append(player1)
    Game.players.append(player2)

    PowerupSpawner.init()
    PowerupSpawner.create_spawn_powerup_event()


def reset():
    Game.reset_game()
    Game.reseting = False
    return (Game.screen,)


def step(actions):
    # Avoid freezing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Game.running = False
            exit()

    keys = []
    # Is this fast?
    keys.extend(pygame.key.get_pressed())
    for i, action in enumerate(actions):
        player = Game.players[i]
        if action[1]:
            keys[player.keys[0]] = True
        if action[2]:
            keys[player.keys[1]] = True

        player.input(keys)

    logic()
    render()

    Game.total_ticks += 1

    return (Game.screen, [Game.players[0].score, Game.players[1].score], Game.reseting, None)


def close():
    pygame.display.quit()
