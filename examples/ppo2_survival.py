import argparse
import time
import os

import tensorflow as tf

from kuruve.envs.SurvivalEnv import SurvivalEnv

from stable_baselines import PPO2
from stable_baselines.common.policies import CnnPolicy
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines.bench import Monitor
from stable_baselines.common.evaluation import evaluate_policy


# Arguments
parser = argparse.ArgumentParser(description="Train survival agent")

group = parser.add_mutually_exclusive_group()
group.add_argument("-play", action="store_true", help="Play with the trained agent")
group.add_argument("-train", action="store_true", help="Train agent")

parser.add_argument("-timesteps", metavar="N", type=int, default=100000)
parser.add_argument("-frameskip", metavar="N", type=int, default=10)
parser.add_argument("-obs_size", metavar="N", type=int, default=96)
parser.add_argument("-envs", metavar="N", type=int, default=1)
parser.add_argument("-model", metavar="name", type=str, default="model_default")

parser.add_argument("-gpu", action="store_true", help="Enable gpu")

args = parser.parse_args()

OBS_SIZE = (args.obs_size, args.obs_size)
FRAMESKIP = args.frameskip
MODEL_NAME = args.model
TIMESTEPS = args.timesteps
ENV_COUNT = args.envs

if args.gpu:
    # GPU Settings
    print("---Using GPU---")
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
else:
    # CPU only
    print("---Using CPU---")
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


def create_env():
    return SurvivalEnv(headless=False, observation_size=OBS_SIZE, fps_cap=60, frameskip=FRAMESKIP,
                       enable_powerups=False, verbose=1)


def create_env_headless():
    return SurvivalEnv(headless=True, observation_size=OBS_SIZE, fps_cap=0, frameskip=FRAMESKIP,
                       enable_powerups=False, verbose=0)


def train():
    #vec_envs = [create_env_headless for i in range(env_count)]
    #vec_envs = SubprocVecEnv(vec_envs)

    if not os.path.isdir("log/"):
        os.mkdir("log")

    if ENV_COUNT == 1:
        envs = create_env_headless()
        env_id = str(time.time())[-6:]
        envs = Monitor(envs, "log/"+MODEL_NAME+"-"+env_id, allow_early_resets=False)
        vec_envs = DummyVecEnv([lambda: envs])
    else:
        vec_envs = []

        def make_env():
            env_id = str(time.time())[-6:]
            env = create_env_headless()
            return Monitor(env, "log/"+MODEL_NAME+"-"+env_id, allow_early_resets=False)
        for _ in range(ENV_COUNT):
            vec_envs.append(make_env)
        vec_envs = SubprocVecEnv(vec_envs)

    model = PPO2('CnnPolicy', vec_envs, verbose=1, ent_coef=0.0001, n_steps=256)
    model.learn(total_timesteps=TIMESTEPS)
    model.save(MODEL_NAME)
    vec_envs.close()

    print("Learning Done!")


def evaluate():
    vec_env = create_env_headless()
    vec_env = DummyVecEnv([lambda: vec_env])

    # Old test
    """
    model = PPO2.load("model_survival_96_10000")
    print("Before Training eval")
    print(evaluate_policy(model, vecEnv, n_eval_episodes=1000))
    print(evaluate_policy(model, vecEnv, n_eval_episodes=1000))
    print(evaluate_policy(model, vecEnv, n_eval_episodes=1000))
    print(evaluate_policy(model, vecEnv, n_eval_episodes=1000))
    """
    model = PPO2.load(MODEL_NAME)
    print("After Training evaluation")
    print(evaluate_policy(model, vec_env, n_eval_episodes=1000))
    print(evaluate_policy(model, vec_env, n_eval_episodes=1000))
    print(evaluate_policy(model, vec_env, n_eval_episodes=1000))
    print(evaluate_policy(model, vec_env, n_eval_episodes=1000))

    vec_env.close()


def play():
    vec_env = create_env()
    vec_env = DummyVecEnv([lambda: vec_env])

    model = PPO2.load(MODEL_NAME)

    obs = vec_env .reset()
    game_count = 0
    while game_count < 1000:
        action = model.predict(obs)[0]
        obs, reward, done, info = vec_env.step(action)
        if done:
            game_count += 1
    vec_env.close()


if __name__ == "__main__":
    if args.train:
        train()
        evaluate()
    elif args.play:
        play()
