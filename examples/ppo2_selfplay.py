import os
import random

import tensorflow as tf

from stable_baselines import PPO2
from stable_baselines.common.policies import CnnPolicy
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv

from kuruve.envs.CompetitiveEnv import CompetitiveEnv

# TODO: Not ready yet.

import numpy as np

import argparse

# Arguments
parser = argparse.ArgumentParser(description="Train selfplaying agent")

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


# Credits to Torille

print("Gpu settings -")
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
print("Gpu settings ----")

MODEL = "model_selfplay_6.zip"

# no input, left, right
possible_actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
OBS_SIZE = (96, 96)
FRAMESKIP = 10

def create_env_headless():
    if os.path.isfile(MODEL):
        opponent_ppo = PPO2.load(MODEL)

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
        if not opponent_ppo.use_random_agent:
            #obs = np.pad(obs[None], ((0, 3), (0, 0)), 'constant')
            action, opponent_ppo.hidden_state = opponent_ppo.predict(obs, state=opponent_ppo.hidden_state)
            return action
        else:
            return random.choice([0, 1, 2])

    def player2_reset():
        opponent_ppo.hidden_state = None
        # With small chance, update the opponent
        if random.random() < 0.01:
            rand = random.random()
            if rand < 0.2:
                # Just random agent
                print("---Loading random agent---")
                opponent_ppo.use_random_agent = True
            elif rand < 0.4:
                # Load some previous model
                print("---Loading old params---")
                opponent_ppo.use_random_agent = False
                load_file = MODEL
                opponent_ppo.load_parameters(load_file)
            else:
                # Load most recent params
                print("---Loading new params---")
                opponent_ppo.load_parameters(MODEL)
                opponent_ppo.use_random_agent = False

    return CompetitiveEnv(headless=True, observation_size=OBS_SIZE, fps_cap=0, frameskip=FRAMESKIP, enable_powerups=False,
                          verbose=0, player2_step=player2_step, player2_reset=player2_reset)


# Lazy copy paste
def create_env():
    if os.path.isfile(MODEL):
        opponent_ppo = PPO2.load(MODEL)

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
        if not opponent_ppo.use_random_agent:
            #obs = np.pad(obs[None], ((0, 3), (0, 0)), 'constant')
            action, opponent_ppo.hidden_state = opponent_ppo.predict(obs, state=opponent_ppo.hidden_state)
            return action
        else:
            return random.choice([0, 1, 2])

    def player2_reset():
        opponent_ppo.hidden_state = None
        # With small chance, update the opponent
        if random.random() < 0.01:
            rand = random.random()
            if rand < 0.2:
                # Just random agent
                print("---Loading random agent---")
                opponent_ppo.use_random_agent = True
            elif rand < 0.4:
                # Load some previous model
                print("---Loading old params---")
                opponent_ppo.use_random_agent = False
                load_file = MODEL
                opponent_ppo.load_parameters(load_file)
            else:
                # Load most recent params
                print("---Loading new params---")
                opponent_ppo.load_parameters(MODEL)
                opponent_ppo.use_random_agent = False

    return CompetitiveEnv(headless=False, observation_size=OBS_SIZE, fps_cap=60, frameskip=FRAMESKIP, enable_powerups=False,
                          verbose=1, player2_step=player2_step, player2_reset=player2_reset)


def train(timesteps=10000, env_count=4):
    envs = [create_env_headless for _ in range(env_count)]
    vec_envs = SubprocVecEnv(envs, start_method="spawn")

    model = PPO2('CnnPolicy', vec_envs, verbose=1, ent_coef=0.00001, n_steps=256)
    #model = PPO2(CnnPolicy, vec_envs, verbose=1, n_steps=256)

    if not os.path.isfile(MODEL):
        model.save(MODEL)
        print("Run again to train")
    else:
        model.learn(total_timesteps=timesteps)
        model.save(MODEL)
        print("Training Done")

    vec_envs.close()
def play():
    vec_env = create_env()
    vec_env = DummyVecEnv([lambda: vec_env])

    # model = PPO2(CnnPolicy, vecEnv, verbose=1, ent_coef=0.0001, n_steps=256)
    # model.load("MODEL_cnn_5.zip", vecEnv)
    model = PPO2.load(MODEL)
    model.set_env(vec_env)

    game_count = 0
    obs = vec_env.reset()

    t = 0
    while game_count < 10000:
        #action = model.predict(obs)[0]
        action = [0]
        #print(obs.shape)
        obs, reward, done, info = vec_env.step(action)
        from PIL import Image

        image = Image.fromarray(obs[0].reshape((96,96)), "L")
        if t > 5 and t < 12:
            #image.convert("L").save("test.bmp")
            #mage.show()
            pass
        t += 1
        if done:
            game_count += 1
            vec_env.reset()

    vec_env.close()


if __name__ == "__main__":

    #train(timesteps=30000000, env_count=4)
    #play()
    print("Hello")
