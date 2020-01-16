from RandomEnv import RandomEnv

from stable_baselines import A2C

from stable_baselines.common.policies import CnnPolicy

from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv

import sys

# TODO: update this file

def create_env():
    return RandomEnv(headless=False, observation_size=(96, 96), fps_cap=0, frameskip=20, enable_powerups=False, verbose=1)


def create_env_headless():
    return RandomEnv(headless=True, observation_size=(96, 96), fps_cap=0, frameskip=20, enable_powerups=False)


def a2c_training(model_name="model_x", timesteps=10000, env_count=4):
    envs = [create_env_headless for _ in range(env_count)]
    vec_env = SubprocVecEnv(envs)

    model = A2C(CnnPolicy, vec_env, verbose=1, ent_coef=0.00001, n_steps=256)
    model.learn(total_timesteps=timesteps)
    model.save(model_name)

    print("Learning Done!")


def a2c_play(model_name="model_x"):
    vec_env = create_env()
    vec_env = DummyVecEnv([lambda: vec_env])

    model = A2C.load(model_name)

    game_count = 0
    obs = vec_env.reset()
    while game_count < 10000:
        action = model.predict(obs)[0]
        obs, reward, done, info = vec_env.step(action)
        if done:
            game_count += 1


if __name__ == "__main__":
    #print(sys.argv)
    #a2c_training("model_a2c_no_idle", 2000000, 8)
    a2c_play("model_a2c_no_idle")
