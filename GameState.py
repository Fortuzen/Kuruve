
# Things that change


class GameState:
    total_ticks = 0
    running = True
    screen = None
    collision_surface = None

    @staticmethod
    def clear_screen(surface):
        surface.fill((0, 0, 0, 255))
