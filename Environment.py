
import pygame
from KurveGame import *
from Powerup import PowerupSpawner


class Env:
    def __init__(self):
        self.small_screen = None
        pass

    def make(self):
        # Hide window, not ready
        # os.putenv('SDL_VIDEODRIVER', 'fbcon')
        # os.environ["SDL_VIDEODRIVER"] = "dummy"

        Game.init()
        Game.framerate = 0
        Game.is_learning_env = True

        # Create smaller surface
        self.small_screen = pygame.Surface((64, 64))

        # player1 = Player(50, 50, 0, (255, 0, 0), "Kurve_1", [pygame.K_LEFT, pygame.K_RIGHT])
        # player2 = Player(500, 500, 180, (0, 255, 0), "Kurve_2", [pygame.K_a, pygame.K_d])
        # Game.players.append(player1)
        # Game.players.append(player2)

        Game.add_player("Kurve_1", (255, 0, 0), [pygame.K_LEFT, pygame.K_RIGHT])
        Game.add_player("Kurve_2", (0, 255, 0), [pygame.K_a, pygame.K_d])

        PowerupSpawner.init()
        PowerupSpawner.create_spawn_powerup_event()

    def reset(self):
        Game.reset_game()
        Game.reseting = False
        return (GameState.screen,)

    def step(self, actions):
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

    def render_env(self):
        pygame.transform.scale(GameState.screen, (64, 64), self.small_screen)
        GameState.screen.blit(self.small_screen, (640-64, 640-64))
        #pygame.display.update()
