# Kuruve by Fortuzen
# Curve fever clone

import pygame
from pygame import gfxdraw
import math
import collections
import random
import copy
import os

from KurveGame import *

from Player import Player


def mainloop():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 32)

    Game.add_player("Kurve_1", (255, 0, 0), [pygame.K_LEFT, pygame.K_RIGHT])
    Game.add_player("Kurve_2", (0, 255, 0), [pygame.K_a, pygame.K_d])
    Game.add_player("Kurve_3", (0, 0, 255), [pygame.K_n, pygame.K_m])

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

    GameConfig.powerups_enabled = False

    # Starts powerup spawning
    if GameConfig.powerups_enabled:
        PowerupSpawner.init()
        PowerupSpawner.create_spawn_powerup_event()

    Game.reset_game()

    while GameState.running:
        Game.game_input()
        Game.game_logic()
        Game.game_render()

        # lock fps
        clock.tick(GameConfig.framerate)

        if len(Game.fpsQueue) == Game.fpsQueue.maxlen:
            Game.fpsQueue.popleft()
        Game.fpsQueue.append(clock.get_fps())

        Game.update_fps_counter()
        GameState.total_ticks += 1


# When run directly
def main():
    Game.init()
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

    Game.init()
    Game.framerate = 0
    Game.is_learning_env = True

    #player1 = Player(50, 50, 0, (255, 0, 0), "Kurve_1", [pygame.K_LEFT, pygame.K_RIGHT])
    #player2 = Player(500, 500, 180, (0, 255, 0), "Kurve_2", [pygame.K_a, pygame.K_d])
    #Game.players.append(player1)
    #Game.players.append(player2)

    Game.add_player("Kurve_1", (255, 0, 0), [pygame.K_LEFT, pygame.K_RIGHT])
    Game.add_player("Kurve_2", (0, 255, 0), [pygame.K_a, pygame.K_d])

    PowerupSpawner.init()
    PowerupSpawner.create_spawn_powerup_event()


def reset():
    Game.reset_game()
    Game.reseting = False
    return (GameState.screen,)


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
        player = Player.players[i]
        if action[1]:
            keys[player.keys[0]] = True
        if action[2]:
            keys[player.keys[1]] = True

        player.input(keys)

    Game.game_logic()
    Game.game_render()

    GameState.total_ticks += 1

    return (GameState.screen, [Player.players[0].score, Player.players[1].score], Game.reseting, None)


def close():
    pygame.display.quit()
