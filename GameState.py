

class GameState:
    """Global variables that can be manipulated by others"""

    total_ticks = 0
    round_ticks = 0
    running = True
    # Redraw whole screen if we pick powerup
    force_redraw = False
    # Pygame surfaces
    screen = None
    collision_surface = None

    # Survival maps
    maps = []
    current_map_index = 0

    @staticmethod
    def clear_screen(surface):
        """Clear surface"""
        surface.fill((0, 0, 0, 255))
