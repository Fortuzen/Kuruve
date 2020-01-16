from RandomEnv import RandomEnv

from stable_baselines import PPO2
from stable_baselines.common.policies import MlpPolicy

from stable_baselines.common.policies import CnnPolicy, CnnLstmPolicy

from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv

# TODO: update this file

def create_env():
    return RandomEnv(headless=False, observation_size=(96, 96), fps_cap=0, frameskip=20, enable_powerups=False)

def create_env_headless():
    return RandomEnv(headless=True, observation_size=(96, 96), fps_cap=0, frameskip=20, enable_powerups=False)


def main():
    env_count = 2
    envs = [create_env for i in range(env_count)]
    vecEnv = SubprocVecEnv(envs)

    #model = PPO2(MlpLstmPolicy, vecEnv, nminibatches=env_count//2, verbose=1)
    #model = PPO2(CnnPolicy, vecEnv, nminibatches=env_count // 2, verbose=1)
    model = PPO2(CnnLstmPolicy, vecEnv, nminibatches=env_count // 2, verbose=1)

    #model = PPO2(MlpPolicy, vecEnv, nminibatches=env_count//2, verbose=1)

    #model = PPO2(CnnPolicy, vecEnv, verbose=1)

    #env = create_env()
    #env = DummyVecEnv([lambda: env])
    #model = PPO2(MlpPolicy, env, verbose=1)
    #model = PPO2(CnnPolicy, env, verbose=1)

    model.learn(total_timesteps=50000)
    model.save("MODEL_2")

    print("Learning Done!")

def mlp_training():
    #env_count = 2
    #envs = [create_env for i in range(env_count)]
    #vecEnv = SubprocVecEnv(envs)
    #model = PPO2(MlpPolicy, vecEnv, nminibatches=env_count // 2, verbose=1)

    vecEnv = create_env_headless()
    vecEnv = DummyVecEnv([lambda: vecEnv])

    policy_kwargs = dict(net_arch=[128, 128])
    model = PPO2(MlpPolicy, vecEnv, policy_kwargs=policy_kwargs, verbose=1)
    model.learn(total_timesteps=100000)
    model.save("MODEL_mlp_custom.zip")

    print("Learning Done!")


def mlp_play():
    vecEnv = create_env()
    vecEnv = DummyVecEnv([lambda: vecEnv])
    policy_kwargs = dict(net_arch=[128, 128])
    model = PPO2(MlpPolicy, vecEnv, policy_kwargs=policy_kwargs, verbose=1)
    model.load("MODEL_mlp_custom.zip", vecEnv)

    game_count = 0
    obs = vecEnv.reset()
    while game_count < 1000:
        action = model.predict(obs)[0]
        #print(action)
        obs, reward, done, info = vecEnv.step(action)
        if done:
            game_count += 1



def cnn_training():
    env_count = 4
    envs = [create_env_headless for i in range(env_count)]
    vecEnv = SubprocVecEnv(envs)

    #model = PPO2(MlpPolicy, vecEnv, nminibatches=env_count // 2, verbose=1)
    #vecEnv = create_env_headless()
    #vecEnv = DummyVecEnv([lambda: vecEnv])
    #vecEnv = VecFrameStack(vecEnv, n_stack=2)
    #policy_kwargs = dict(net_arch=[256, 128])

    model = PPO2(CnnPolicy, vecEnv, verbose=1, ent_coef=0.0001, n_steps=256)
    #model = PPO2(CnnPolicy, vecEnv, verbose=1, ent_coef=0.1, n_steps=256)
    model.learn(total_timesteps=1000)
    model.save("MODEL_cnn_7")

    print("Learning Done!")

def cnn_play():
    vecEnv = create_env()
    vecEnv = DummyVecEnv([lambda: vecEnv])

    #vecEnv = VecFrameStack(vecEnv, n_stack=2)
    #policy_kwargs = dict(net_arch=[256, 128])

    #model = PPO2(CnnPolicy, vecEnv, verbose=1, ent_coef=0.0001, n_steps=256)
    #model.load("MODEL_cnn_5.zip", vecEnv)
    model = PPO2.load("MODEL_cnn_6")

    frameskip = 20

    game_count = 0
    obs = vecEnv.reset()
    while game_count < 10000:
        action = model.predict(obs)[0]
        obs, reward, done, info = vecEnv.step(action)
        if done:
            game_count += 1


def run_model():
    env = create_env()
    env = DummyVecEnv([lambda: env])
    model = PPO2(MlpPolicy, env, verbose=1)
    model.load("MODEL_2", env)

    #env_count = 2
    #envs = [create_env for i in range(env_count)]
    #vecEnv = SubprocVecEnv(envs)
    #model = PPO2(MlpLstmPolicy, vecEnv, verbose=1, nminibatches=env_count//2)
    #model.load("MODEL_2", vecEnv)

    epos = 10
    iters = 10000

    for epo in range(0, epos):
        obs = env.reset()

        print("New epoch")
        for i in range(0, iters):
            action = model.predict(obs)[0]
            obs, reward, done, info = env.step(action)


if __name__ == "__main__":
    #main()
    #mlp_training()
    #mlp_play()
    #cnn_training()
    cnn_play()
    #run_model()
