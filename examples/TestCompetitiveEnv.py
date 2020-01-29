import random

from kuruve.envs.CompetitiveEnv import CompetitiveEnv
from PIL import Image

""" Test self-play environment"""


# no input, left, right
possible_actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
OBS_SIZE = (96, 96)
FRAMESKIP = 14


def create_env():
    def player2_step(obs):
        return random.choice([0, 1, 2])

    def player2_reset():
        pass

    return CompetitiveEnv(headless=False, observation_size=OBS_SIZE, fps_cap=60, frameskip=FRAMESKIP, enable_powerups=False,
                          verbose=1, player2_step=player2_step, player2_reset=player2_reset)


def play():
    vec_env = create_env()

    game_count = 0
    obs = vec_env.reset()
    t = 0
    while game_count < 10:
        action = 0

        obs, reward, done, info = vec_env.step(action)

        if 10 < t < 12:
            image1 = Image.fromarray(obs[..., 0], "L")
            image2 = Image.fromarray(obs[..., 1], "L")
            #image.convert("L").save("test.bmp")
            #Image.blend(image1, image2, 0.5).show()
            #image1.show()
            #image2.show()
            image1.save("comp_env_1.png")
            image2.save("comp_env_2.png")
        t += 1
        if done:
            game_count += 1
            vec_env.reset()

    vec_env.close()


if __name__ == "__main__":
    play()
