import pygame  # hmmm


class GameConfig:
    """
    Settings that should be set before the game and should not be changed

    :cvar int screen_x: Screen width
    :cvar int screen_y: Screen height
    :cvar int framerate: Max framerate
    :cvar bool headless: Do not create window
    :cvar (int,int) wormhole_timer_range: How often create wormholes. Smaller values = More often.
    :cvar bool powerups_enabled: Enable powerups.
    :cvar [string] powerup_blacklist: Disable named powerups.
    :cvar bool survival: Enable survival gamemode
    :cvar string survival_maps_folder: Survival mode maps folder
    :cvar [[pygame.keycode, pygame.keycode]] default_controls: Controls for players
    :cvar [(int, int, int)] default_colors: Colors for players.


    """

    screen_x = 640  # Default screen size (640, 640)
    screen_y = 640
    framerate = 60  # Default fps 60
    headless = False  # Create window or not

    # "short godmode" now and then, as in frames. Frequency of the wormhole
    wormhole_timer_range = (60, 120)

    powerups_enabled = True
    powerup_blacklist = []  # Ignored powerups

    survival = False  # Singleplayer mode
    survival_maps_folder = "maps/"

    # These are for players
    default_controls = [[pygame.K_LEFT, pygame.K_RIGHT], [pygame.K_a, pygame.K_s],
                        [pygame.K_v, pygame.K_b], [pygame.K_k, pygame.K_l]]

    default_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255)]
