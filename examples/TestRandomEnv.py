from kuruve.envs.RandomEnv import RandomEnv

"""Test random environment"""

def create_env():
    return RandomEnv(headless=False, observation_size=(96, 96), fps_cap=0, frameskip=20, enable_powerups=False)


def create_env_headless():
    return RandomEnv(headless=True, observation_size=(96, 96), fps_cap=0, frameskip=20, enable_powerups=False)


def test():
    env = create_env()
    obs = env.reset()
    for _ in range(1000):
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)

    env.close()

    env = create_env_headless()
    obs = env.reset()
    for _ in range(1000):
        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)
    env.close()


if __name__ == "__main__":
    test()
