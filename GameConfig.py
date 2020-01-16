import pygame  # hmmm


class GameConfig:
    """Settings that should be set before the game and should not be changed"""

    screen_x = 640  # Default screen size (640, 640)
    screen_y = 640
    framerate = 60  # Default fps 60
    headless = False  # Create window or not

    wormhole_timer_range = (60, 120)  # "short godmode", as in frames

    powerups_enabled = True
    powerup_blacklist = []  # Ignored powerups

    survival = False  # Singleplayer mode
    survival_maps_folder = "maps/"

    # These are for players
    default_controls = [[pygame.K_LEFT, pygame.K_RIGHT], [pygame.K_a, pygame.K_s],
                        [pygame.K_v, pygame.K_b], [pygame.K_k, pygame.K_l]]

    default_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255)]
