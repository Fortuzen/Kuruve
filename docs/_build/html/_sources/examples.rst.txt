.. _examples:

Examples
==================================

There are several examples on how to use the environment. Check the examples folder for other examples.

Basic example
----------------------------------
Simple example of running the environment

.. code-block:: python

   from kuruve.envs.GymEnv import KuruveGymEnv
   from kuruve.KurveGame import *

   env = KuruveGymEnv(headless=False, observation_size=(96, 96), fps_cap=0, frameskip=1, enable_powerups=False, verbose=0)
   obs = env.reset()
   for _ in range(1000):
       actions = env.action_space.sample()
       obs, reward, done, info = env.step(actions)
   env.close()


Stable-Baselines Survival
----------------------------------
.. code-block:: python

    from kuruve.envs.SurvivalEnv import SurvivalEnv

    from stable_baselines import PPO2
    from stable_baselines.common.policies import CnnPolicy
    from stable_baselines.common.vec_env import DummyVecEnv, SubprocVecEnv
    from stable_baselines.bench import Monitor
    from stable_baselines.common.evaluation import evaluate_policy

    def create_env():
        return SurvivalEnv(headless=False, observation_size=OBS_SIZE, fps_cap=60, frameskip=FRAMESKIP,
                        enable_powerups=False, verbose=0)


    def create_env_headless():
        return SurvivalEnv(headless=True, observation_size=OBS_SIZE, fps_cap=0, frameskip=FRAMESKIP,
                        enable_powerups=False, verbose=0)

    if __name__ == "__main__":
        # Train model
        env = create_env_headless()
        vec_env = DummyVecEnv([lambda: env])
        model = PPO2('CnnPolicy', vec_env, verbose=1, ent_coef=0.0001, n_steps=256)
        model.learn(total_timesteps=100000)
        model.save("Example_Model")
        # Important on linux
        vec_env.close()

        # Run model
        env = create_env()
        vec_env = DummyVecEnv([lambda: env])
        model = PPO2.load("Example_Model")
        obs = vec_env.reset()
        game_count = 0
        while game_count < 1000:
            action = model.predict(obs)[0]
            obs, reward, done, info = vec_env.step(action)
            if done:
                game_count += 1
                
        vec_env.close()