import os
import random
import time
from glob import glob
from pprint import pprint
from datetime import datetime
import argparse
import tensorflow as tf
from kuruve.envs.SimpleAiEnv import SimpleAiEnv
from stable_baselines import PPO2
from stable_baselines.common.policies import CnnPolicy
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines.common.evaluation import evaluate_policy
from stable_baselines.bench import Monitor

import numpy as np

# Arguments
parser = argparse.ArgumentParser(description="Train selfplaying agent")

group = parser.add_mutually_exclusive_group()
group.add_argument("-play", action="store_true", help="Play with the trained agent")
group.add_argument("-train", action="store_true", help="Train agent")

parser.add_argument("-timesteps", metavar="N", type=int, default=100000)
parser.add_argument("-frameskip", metavar="N", type=int, default=10)
parser.add_argument("-obs_size", metavar="N", type=int, default=96)
parser.add_argument("-envs", metavar="N", type=int, default=1)
parser.add_argument("-model", metavar="name", type=str, default="model.pkl")

parser.add_argument("-gpu", action="store_true", help="Enable gpu")

args = parser.parse_args()

OBS_SIZE = (args.obs_size, args.obs_size)
FRAMESKIP = args.frameskip
MODEL_NAME = args.model
TIMESTEPS = args.timesteps
ENV_COUNT = args.envs

n_steps = 0

if args.gpu:
    if __name__ == "__main__":
        # GPU Settings
        print("---Using GPU---")
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.Session(config=config)
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
else:
    # CPU only
    print("---Using CPU---")
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


def create_env_headless():
    return SimpleAiEnv(headless=True, observation_size=OBS_SIZE, fps_cap=0, frameskip=FRAMESKIP, enable_powerups=False,
                       verbose=0, ai_count=1)


def create_env_headless_monitor():
    env = SimpleAiEnv(headless=True, observation_size=OBS_SIZE, fps_cap=0, frameskip=FRAMESKIP, enable_powerups=False,
                verbose=0, ai_count=1)
    os.makedirs("log/", exist_ok=True)
    return Monitor(env, "log/" + str(os.getpid()), allow_early_resets=False)


def create_env():
    return SimpleAiEnv(headless=False, observation_size=OBS_SIZE, fps_cap=0, frameskip=FRAMESKIP, enable_powerups=False,
                       verbose=1, ai_count=1)


def train():

    def callback(_locals, _globals):
        global n_steps
        if (n_steps + 1) % 100 == 0:
            _locals['self'].save(MODEL_NAME)
        n_steps += 1

    envs = [create_env_headless_monitor for _ in range(ENV_COUNT)]
    envs = SubprocVecEnv(envs, start_method="spawn")

    #policy_kwargs = dict(act_fun=tf.nn.relu, net_arch=[128, 128, "lstm"], n_lstm=128)
    #model = PPO2('CnnLstmPolicy', vec_envs, verbose=1, ent_coef=0.0001, n_steps=256, nminibatches=ENV_COUNT // 2, policy_kwargs=policy_kwargs)
    model = PPO2('CnnPolicy', envs, verbose=1, ent_coef=0.00001, n_steps=256)

    model.learn(total_timesteps=TIMESTEPS, callback=callback)
    model.save(MODEL_NAME)
    print("Training Done")
    envs.close()


def play():
    vec_env = create_env()
    vec_env = DummyVecEnv([lambda: vec_env])

    # model = PPO2(CnnPolicy, vecEnv, verbose=1, ent_coef=0.0001, n_steps=256)
    # model.load("MODEL_cnn_5.zip", vecEnv)
    model = PPO2.load(MODEL_NAME)
    model.set_env(vec_env)

    game_count = 0
    obs = vec_env.reset()

    wins = 0
    while game_count < 100:
        action = model.predict(obs)[0]
        obs, reward, done, info = vec_env.step(action)
        if done:
            game_count += 1
            if reward == 1:
                wins += 1
            vec_env.reset()
    print(wins / game_count)
    vec_env.close()


if __name__ == "__main__":
    if args.train:
        train()
    elif args.play:
        play()
