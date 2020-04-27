from kuruve.envs.RandomEnv import RandomEnv

"""Test random environment"""


def create_env():
    return RandomEnv(headless=False, observation_size=(96, 96), fps_cap=0, frameskip=10, enable_powerups=False,
                     random_players=3)


def create_env_headless():
    return RandomEnv(headless=True, observation_size=(96, 96), fps_cap=0, frameskip=10, enable_powerups=False,
                     random_players=1)


def play():
    # Environment with a window
    env = create_env()
    obs = env.reset()
    for _ in range(500):
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
    env.close()

    # Environment without a window
    env = create_env_headless()
    obs = env.reset()
    for _ in range(500):
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
    env.close()


if __name__ == "__main__":
    play()
