# Kuruve by Fortuzen
# Curve fever clone

"""Run this if you just want to play"""


from KurveGame import *
from GameConfig import GameConfig
from GameState import GameState


def mainloop():
    font = pygame.font.SysFont(None, 32)

    Game.add_player("Kurve_1", GameConfig.default_colors[0], GameConfig.default_controls[0])
    Game.add_player("Kurve_2", GameConfig.default_colors[1], GameConfig.default_controls[1])
    #Game.add_player("Kurve_3", GameConfig.default_colors[2], GameConfig.default_controls[2])
    #Game.add_player("Kurve_4", GameConfig.default_colors[3], GameConfig.default_controls[3])

    # Game begins
    Game.reset_game()

    while GameState.running:
        Game.game_input()
        Game.game_logic()
        Game.game_render()

        if len(Game.fpsQueue) == Game.fpsQueue.maxlen:
            Game.fpsQueue.popleft()
        Game.fpsQueue.append(Game.clock.get_fps())
        Game.update_fps_counter()

    Game.close()


# When run directly
def main():
    GameConfig.headless = False
    #GameConfig.survival = True
    #GameConfig.framerate = 0
    GameConfig.powerups_enabled = False
    GameConfig.powerup_blacklist = ["gspeed", "gslow", "gthin", "ggod", "rspeed", "rslow", "rthick", "rturn"]
    Game.init()
    mainloop()


if __name__ == "__main__":
    main()

