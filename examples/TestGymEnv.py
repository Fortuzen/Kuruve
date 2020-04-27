from kuruve.envs.GymEnv import KuruveGymEnv
from kuruve.GameConfig import GameConfig
import cv2


"""Testing GymEnvironment and show image of the observation"""

GameConfig.powerup_blacklist = ["gspeed", "gslow", "gthin", "ggod", "rspeed", "rslow", "rthick", "rturn"]
env = KuruveGymEnv(headless=False, observation_size=(80, 80), fps_cap=0, frameskip=1, enable_powerups=True, verbose=0,
                   player_count=2)

show_obs = True
obs = env.reset()
for _ in range(100000):
    actions = env.action_space.sample()
    obs, reward, done, info = env.step(actions)
    if show_obs:
        cv2.imshow('frame', obs)
env.close()

# Create headless environment environment

env2 = KuruveGymEnv(headless=True, observation_size=(128, 128), fps_cap=0, frameskip=20, enable_powerups=False, verbose=1)
obs = env2.reset()
for t in range(1000):
    actions = env2.action_space.sample()
    obs, reward, done, info = env2.step(actions)

env2.close()
