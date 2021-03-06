import pygame
import collections
import random
import os

from .Powerup import PowerupSpawner, Powerup
from .Event import EventManager
from .Player import Player

from .GameState import GameState
from .GameConfig import GameConfig


def load_survival_maps():
    print(os.path.dirname(__file__))
    path = os.path.dirname(__file__) + "/" + GameConfig.survival_maps_folder
    files = os.listdir(path)
    for file in files:
        if file not in GameState.maps:
            GameState.maps.append(pygame.image.load(path + file))

    GameState.current_map_index = 0


class Game:
    """Class that contains the main functionality of the game but not the main loop"""

    avg_fps = 0
    fpsQueue = collections.deque(maxlen=100)
    clock = None

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
        # Dont update every tick
        if GameState.round_ticks % 60 == 0:
            pygame.display.set_caption(str(fps))

    @staticmethod
    def reset_game():
        """ Reset the game"""

        GameState.screen.fill((0, 0, 0, 255))
        GameState.collision_surface.fill((0, 0, 0, 255))

        thick = 4
        pygame.draw.rect(GameState.screen, (255, 255, 0), (0, 0, GameConfig.screen_x-1, GameConfig.screen_y-1), thick)
        pygame.draw.rect(GameState.collision_surface, (255, 255, 0),
                         (0, 0, GameConfig.screen_x-1, GameConfig.screen_y-1), thick)

        if GameConfig.survival:
            GameState.current_map_index = random.randint(0, len(GameState.maps)-1)
            GameState.screen.blit(GameState.maps[GameState.current_map_index], (0, 0))
            GameState.collision_surface.blit(GameState.maps[GameState.current_map_index], (0, 0))

        # Reset players
        for player in Player.players:
            # TODO: Prevent player spawning at bad spots (aka immediate lose)
            player.position[0] = random.randint(50, 500)
            player.position[1] = random.randint(50, 500)
            player.angle = random.randint(0, 360)
            player.alive = True
            # TODO: maybe change to radius modifier
            player.radius = 3

            player.speedModifier = 1.0
            player.godmode = False
            player.turn90 = False
            player.turnAmount = 4.0

            # Prevent player from losing at the start
            if GameConfig.survival:
                while True:
                    if GameState.collision_surface.get_at((player.position[0], player.position[1])) == (0, 0, 0):
                        break
                    else:
                        player.position[0] = random.randint(50, 500)
                        player.position[1] = random.randint(50, 500)

        EventManager.events = []
        Powerup.powerups = []

        if GameConfig.powerups_enabled and not GameConfig.survival:
            PowerupSpawner.create_spawn_powerup_event()

        Game.reseting = False
        GameState.round_ticks = 0

    @staticmethod
    def add_score_alive_players():
        """Add 1 score to the alive players"""

        for player in Player.players:
            if player.alive:
                player.score += 1

    @staticmethod
    def init():
        """Initialize the game. Must be called before every other game related function."""

        pygame.init()
        pygame.font.init()
        # Uninit sound because it is not needed
        pygame.mixer.quit()

        # We must force 32 format screen on some systems
        if GameConfig.headless:
            os.putenv('SDL_VIDEODRIVER', 'fbcon')
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.init()
            GameState.screen = pygame.Surface((GameConfig.screen_x, GameConfig.screen_y))
            GameState.screen = GameState.screen.convert(32, 0)
            # Ignore other pygame events
            pygame.event.set_allowed([pygame.QUIT])
        else:
            GameState.screen = pygame.display.set_mode((GameConfig.screen_x, GameConfig.screen_y), 0, 32)
            pygame.display.set_caption("Kuruve")

        GameState.collision_surface = pygame.Surface((GameConfig.screen_x, GameConfig.screen_y))
        GameState.collision_surface = GameState.collision_surface.convert(32, 0)

        Game.clock = pygame.time.Clock()
        Powerup.font = pygame.font.SysFont("comicsansms", 36)
        GameState.total_ticks = 0
        Player.players = []

        # Load survival levels
        if GameConfig.survival:
            load_survival_maps()

        # Starts powerup spawning
        if GameConfig.powerups_enabled and not GameConfig.survival:
            PowerupSpawner.init()
            PowerupSpawner.create_spawn_powerup_event()

        Game.reset_game()

    @staticmethod
    def close():
        """Quit pygame"""

        EventManager.events = []
        GameState.total_ticks = 0
        Player.players = []
        Powerup.powerups = []
        PowerupSpawner.available_powerups = []
        # This fixes a crash related to reinitialization
        del Powerup.font

        pygame.display.quit()
        pygame.quit()

    @staticmethod
    def game_input():
        """Process inputs from the user and handle pygame's events"""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameState.running = False

        keys = pygame.key.get_pressed()
        for player in Player.players:
            player.input(keys)

    @staticmethod
    def game_logic():
        """The game's main logic"""

        # Process events
        EventManager.process_events(GameState.total_ticks)

        # Player updates
        for player in Player.players:
            if not player.alive or Game.reseting:
                continue

            player.update()
            # Player collisions
            current_screen = GameState.collision_surface.get_at(player.pixel_collider)
            if current_screen != (0, 0, 0) and player.wormhole_timer >= 0 and not player.godmode:  # make better
                player.alive = False
                Game.add_score_alive_players()
            # Powerup collisions
            for pu in Powerup.powerups:
                if pu.check_collision(player):
                    pu.handle_collision(player)
                    Powerup.powerups.remove(pu)
                    # Redraw whole screen
                    GameState.force_redraw = True
                    break

        # Check alive players if the game is not reseting
        if not Game.reseting:
            c = len(Player.players)
            for player in Player.players:
                if not player.alive:
                    c -= 1
            # If one/zero players alive, reset the game
            if c <= 1:
                if GameConfig.survival and c <= 0:
                    Game.reseting = True
                    # Reset the game on next tick
                    EventManager.fire_event_after_delay(1, Game.reset_game)
                elif not GameConfig.survival:
                    Game.reseting = True
                    # Reset the game on next tick
                    EventManager.fire_event_after_delay(1, Game.reset_game)

    @staticmethod
    def game_render():
        """Render everything. Essential part of collision detection."""

        for player in Player.players:
            player.render(GameState.screen, GameState.collision_surface)

        # Update whole screen (eg when picking up a powerup)
        if GameState.force_redraw:
            GameState.screen.blit(GameState.collision_surface, (0, 0))
            pygame.draw.rect(GameState.screen, (255, 255, 0), (0, 0, 640, 640), 4)
            pygame.draw.rect(GameState.collision_surface, (255, 255, 0), (0, 0, 640, 640), 4)
            GameState.force_redraw = False

        for player in Player.players:
            player.render_yellow_dot(GameState.screen)

        for powerup in Powerup.powerups:
            powerup.render(GameState.screen)

        # Update the actual game window if not in headless mode
        if not GameConfig.headless:
            pygame.display.flip()

        Game.clock.tick(GameConfig.framerate)
        GameState.total_ticks += 1
        GameState.round_ticks += 1

    @staticmethod
    def add_player(name, color, controls, is_ai=False):
        """
        Add a player to the game
        :param name: Player's name
        :param color: Player's color
        :type color: tuple eg (R,G,B)
        :param controls: Player's keyboard controls
        :type controls: A list of pygame keycodes eg [pygame.K_LEFT, pygame.K_RIGHT]
        :param is_ai: Enable (very) simple ai.
        """
        player = Player(0, 0, 0, color, name, controls, is_ai)
        Player.players.append(player)
