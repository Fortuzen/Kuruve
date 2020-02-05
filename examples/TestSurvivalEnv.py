from kuruve.envs.SurvivalEnv import SurvivalEnv
import time

"""Test survival environment"""


OBS_SIZE = (96, 96)
FRAMESKIP = 1


def create_env():
    return SurvivalEnv(headless=False, observation_size=OBS_SIZE, fps_cap=0, frameskip=FRAMESKIP,
                       enable_powerups=False, verbose=1)


def create_env_headless():
    return SurvivalEnv(headless=True, observation_size=OBS_SIZE, fps_cap=0, frameskip=FRAMESKIP,
                       enable_powerups=False, verbose=0)


def test():
    env = create_env()
    obs = env.reset()
    game_count = 0
    while game_count < 100:
        action = env.action_space.sample()
        # Framerate
        #t1 = time.time()
        obs, reward, done, info = env.step(action)
        #try:
        #    print(1/(time.time()-t1))
        #except ZeroDivisionError:
        #    pass

        if done:
            game_count += 1

    env.close()


if __name__ == "__main__":
    test()
