from kuruve.envs.SurvivalEnv import SurvivalEnv

"""Test survival environment"""


OBS_SIZE = (96, 96)
FRAMESKIP = 15


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
        obs, reward, done, info = env.step(action)
        if done:
            game_count += 1

    env.close()


if __name__ == "__main__":
    test()
