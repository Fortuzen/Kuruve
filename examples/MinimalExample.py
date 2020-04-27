from kuruve.envs.GymEnv import KuruveGymEnv
from kuruve.KurveGame import *

env = KuruveGymEnv(headless=False, observation_size=(96, 96), fps_cap=0, frameskip=1, enable_powerups=False, verbose=0)
obs = env.reset()
for _ in range(1000):
    actions = env.action_space.sample()
    obs, reward, done, info = env.step(actions)
env.close()
