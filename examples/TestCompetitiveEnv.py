from kuruve.envs.CompetitiveEnv import CompetitiveEnv
from kuruve.KurveGame import *
from PIL import Image
import cv2

""" Test self-play environment and draw observations"""


# no input, left, right
possible_actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
OBS_SIZE = (80, 80)
FRAMESKIP = 10


def create_env():
    def player2_step(obs):
        return [random.choice([0, 1, 2])]

    def player2_reset():
        pass

    return CompetitiveEnv(headless=True, observation_size=OBS_SIZE, fps_cap=60, frameskip=FRAMESKIP, enable_powerups=False,
                          verbose=1, player2_step=player2_step, player2_reset=player2_reset)


def play():
    vec_env = create_env()
    game_count = 0
    obs = vec_env.reset()
    t = 0
    while game_count < 100:
        action = [random.choice([0, 1, 2])]
        obs, reward, done, info = vec_env.step(action)
        cv2.imshow("frame1", obs[..., 0])
        cv2.imshow("frame2", obs[..., 1])

        # Save observations at some point
        if t==12:
            image1 = Image.fromarray(obs[..., 0], "L")
            image2 = Image.fromarray(obs[..., 1], "L")
            image1.save("comp_env_1.png")
            image2.save("comp_env_2.png")
        t += 1
        if done:
            game_count += 1
            vec_env.reset()
    vec_env.close()


if __name__ == "__main__":
    play()
