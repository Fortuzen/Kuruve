import os
import random
import time
from glob import glob
from pprint import pprint
from datetime import datetime
import argparse
import tensorflow as tf
from kuruve.envs.CompetitiveEnv import CompetitiveEnv
from stable_baselines import PPO2
from stable_baselines.common.policies import CnnPolicy
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines.common.evaluation import evaluate_policy

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
parser.add_argument("-snapshot_time", type=int, default=21600,
                    help="Time in seconds between saving snapshots (default: 3h)")

parser.add_argument("-gpu", action="store_true", help="Enable gpu")

args = parser.parse_args()

OBS_SIZE = (args.obs_size, args.obs_size)
FRAMESKIP = args.frameskip
MODEL_NAME = args.model
TIMESTEPS = args.timesteps
ENV_COUNT = args.envs


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

# Credits to Torille

# no input, left, right
possible_actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def create_env_headless():
    if os.path.isfile(MODEL_NAME):
        opponent_ppo = PPO2.load(MODEL_NAME)

        # Create assign ops for the oppoennt
        with opponent_ppo.graph.as_default():
            update_ops = []
            update_placeholders = []
            for param in opponent_ppo.params:
                placeholder = tf.placeholder(dtype=param.dtype, shape=param.shape)
                update_ops.append(param.assign(placeholder))
                update_placeholders.append(placeholder)
            # Throw them into the agent to have them around the code
            opponent_ppo.param_update_ops = update_ops
            opponent_ppo.param_update_phs = update_placeholders

        # Include the hidden state in the opponent agent
        opponent_ppo.hidden_state = None
        opponent_ppo.use_random_agent = False

    def player2_step(obs):
        action, opponent_ppo.hidden_state = opponent_ppo.predict(obs, state=opponent_ppo.hidden_state)
        return action

    def player2_reset():
        opponent_ppo.hidden_state = None
        print("---Loading new params---")
        opponent_ppo.load_parameters(MODEL_NAME)

    return CompetitiveEnv(headless=True, observation_size=OBS_SIZE, fps_cap=0, frameskip=FRAMESKIP,
                          enable_powerups=False,
                          verbose=0, player2_step=player2_step, player2_reset=player2_reset)


# Lazy copy paste
def create_env():
    if os.path.isfile(MODEL_NAME):
        opponent_ppo = PPO2.load(MODEL_NAME)

        # Create assign ops for the oppoennt
        with opponent_ppo.graph.as_default():
            update_ops = []
            update_placeholders = []
            for param in opponent_ppo.params:
                placeholder = tf.placeholder(dtype=param.dtype, shape=param.shape)
                update_ops.append(param.assign(placeholder))
                update_placeholders.append(placeholder)
            # Throw them into the agent to have them around the code
            opponent_ppo.param_update_ops = update_ops
            opponent_ppo.param_update_phs = update_placeholders

        # Include the hidden state in the opponent agent
        opponent_ppo.hidden_state = None
        opponent_ppo.use_random_agent = False

    def player2_step(obs):
        action, opponent_ppo.hidden_state = opponent_ppo.predict(obs, state=opponent_ppo.hidden_state)
        return action

    def player2_reset():
        opponent_ppo.hidden_state = None
        opponent_ppo.load_parameters(MODEL_NAME)

    return CompetitiveEnv(headless=False, observation_size=OBS_SIZE, fps_cap=60, frameskip=FRAMESKIP,
                          enable_powerups=False,
                          verbose=1, player2_step=player2_step, player2_reset=player2_reset)


def train():
    global last_snapshot_time
    last_snapshot_time = time.time()

    def callback(_locals, _globals):
        global last_snapshot_time
        # Save model
        _locals['self'].save(MODEL_NAME)

    envs = [create_env_headless for _ in range(ENV_COUNT)]
    vec_envs = SubprocVecEnv(envs, start_method="spawn")

    policy_kwargs = dict(act_fun=tf.nn.relu, net_arch=[128, 128])
    model = PPO2('CnnPolicy', vec_envs, verbose=1, ent_coef=0.001, n_steps=256, policy_kwargs=policy_kwargs)
    # model = PPO2('MlpPolicy', vec_envs, verbose=1, ent_coef=0.00001, n_steps=256)
    # model = PPO2(CnnPolicy, vec_envs, verbose=1, n_steps=256)

    if not os.path.isfile(MODEL_NAME):
        model.save(MODEL_NAME)
        print("Run again to train")
        vec_envs.close()
    else:
        model.learn(total_timesteps=TIMESTEPS, callback=callback)
        model.save(MODEL_NAME)
        print("Training Done")
        vec_envs.close()

        # Evaluation
        print("Evalution")
        vec_env = create_env_headless()
        vec_env = DummyVecEnv([lambda: vec_env])
        model = PPO2.load(MODEL_NAME)
        print("After Training evaluation")
        print(evaluate_policy(model, vec_env, n_eval_episodes=100))
        print(evaluate_policy(model, vec_env, n_eval_episodes=100))
        vec_env.close()


def play():
    vec_env = create_env()
    vec_env = DummyVecEnv([lambda: vec_env])

    # model = PPO2(CnnPolicy, vecEnv, verbose=1, ent_coef=0.0001, n_steps=256)
    # model.load("MODEL_cnn_5.zip", vecEnv)
    model = PPO2.load(MODEL_NAME)
    model.set_env(vec_env)

    game_count = 0
    obs = vec_env.reset()

    t = 0
    while game_count < 10000:
        action = model.predict(obs)[0]
        obs, reward, done, info = vec_env.step(action)
        if done:
            game_count += 1
            vec_env.reset()

    vec_env.close()


if __name__ == "__main__":
    if args.train:
        train()
    elif args.play:
        play()
