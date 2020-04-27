from kuruve.envs.RandomEnv import RandomEnv
import os
from stable_baselines import PPO2
from stable_baselines.common.policies import CnnPolicy
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv


def create_env():
    return RandomEnv(headless=False, observation_size=(96, 96), fps_cap=60, frameskip=10, enable_powerups=False)


def create_env_headless():
    return RandomEnv(headless=True, observation_size=(96, 96), fps_cap=0, frameskip=10, enable_powerups=False)


def cnn_training(model_name="model_random", timesteps=10000, env_count=4):
    envs = [create_env_headless for _ in range(env_count)]
    vec_env = SubprocVecEnv(envs)

    model = PPO2(CnnPolicy, vec_env, verbose=1, ent_coef=0.0001, n_steps=256)
    model.learn(total_timesteps=timesteps)

    if not os.path.exists("models"):
        os.makedirs("models")

    model.save("models/"+model_name)
    print("Learning Done!")


def cnn_play(model_name="model_random"):
    vec_env = create_env()
    vec_env = DummyVecEnv([lambda: vec_env])
    model = PPO2.load(model_name)

    game_count = 0
    obs = vec_env.reset()
    while game_count < 10000:
        action = model.predict(obs)[0]
        obs, reward, done, info = vec_env.step(action)
        if done:
            game_count += 1


if __name__ == "__main__":
    cnn_training("model_random", 10000, 1)
    cnn_play("model_random")
