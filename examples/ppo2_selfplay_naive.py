import os
import time
import argparse
import tensorflow as tf
from kuruve.envs.CompetitiveEnv import CompetitiveEnv
from stable_baselines import PPO2
from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines.common.evaluation import evaluate_policy


# Arguments
parser = argparse.ArgumentParser(description="Train selfplaying agent")

group = parser.add_mutually_exclusive_group()
group.add_argument("--play", action="store_true", help="Play with the trained agent")
group.add_argument("--train", action="store_true", help="Train agent")

parser.add_argument("-timesteps", metavar="N", type=int, default=100000)
parser.add_argument("-frameskip", metavar="N", type=int, default=10)
parser.add_argument("-obs_size", metavar="N", type=int, default=96)
parser.add_argument("-envs", metavar="N", type=int, default=1)
parser.add_argument("-model", metavar="name", type=str, default="model.pkl")

parser.add_argument("--gpu", action="store_true", help="Enable gpu")

args = parser.parse_args()

OBS_SIZE = (args.obs_size, args.obs_size)
FRAMESKIP = args.frameskip
MODEL_NAME = args.model
TIMESTEPS = args.timesteps
ENV_COUNT = args.envs

possible_actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # no input, left, right

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
    # Credits to Torille
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

    return CompetitiveEnv(headless=True, observation_size=OBS_SIZE, fps_cap=0, frameskip=FRAMESKIP,
                          enable_powerups=False,
                          verbose=0, player2_step=player2_step, player2_reset=player2_reset)


# Lazy copy paste
def create_env():
    if os.path.isfile(MODEL_NAME):
        opponent_ppo = PPO2.load(MODEL_NAME)
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
    def callback(_locals, _globals):
        # Save model
        _locals['self'].save(MODEL_NAME)

    envs = [create_env_headless for _ in range(ENV_COUNT)]
    vec_envs = SubprocVecEnv(envs)
    model = PPO2('CnnPolicy', vec_envs, verbose=1, ent_coef=0.0001, n_steps=256)

    if not os.path.isfile(MODEL_NAME):
        model.save(MODEL_NAME)
        vec_envs.close()
        print("Run again to train")
    else:
        model.learn(total_timesteps=TIMESTEPS, callback=callback)
        model.save(MODEL_NAME)
        vec_envs.close()
        print("Training Done")

        # Evaluation
        print("Evaluation")
        vec_env = create_env_headless()
        vec_env = DummyVecEnv([lambda: vec_env])
        model = PPO2.load(MODEL_NAME)
        print(evaluate_policy(model, vec_env, n_eval_episodes=100))
        print(evaluate_policy(model, vec_env, n_eval_episodes=100))
        vec_env.close()


def play():
    vec_env = create_env()
    vec_env = DummyVecEnv([lambda: vec_env])

    model = PPO2.load(MODEL_NAME)
    model.set_env(vec_env)

    game_count = 0
    obs = vec_env.reset()

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
