from kuruve.envs.GymEnv import KuruveGymEnv
from kuruve.GameConfig import GameConfig

from PIL import Image
import cv2
import time

"""Testing GymEnvironment and show image of the observation"""

GameConfig.powerup_blacklist = ["gspeed", "gslow", "gthin", "ggod", "rspeed", "rslow", "rthick", "rturn"]
env = KuruveGymEnv(headless=False, observation_size=(96, 96), fps_cap=0, frameskip=1, enable_powerups=True, verbose=0,
                   player_count=2)

show_obs = True
obs = env.reset()
t = 0
for _ in range(100000):
    actions = env.action_space.sample()

    obs, reward, done, info = env.step(actions)
    #print(Game.clock.get_fps())

    if show_obs:
        image = Image.fromarray(obs, "RGB")
        if 15 < t < 17:
            #image.show()
            #image.save("img.bmp")
            print("img created")
        #img = cv2.imread(obs)
        cv2.imshow('frame', obs)
        t += 1
env.close()

import sys
sys.exit()

# Create environment headless environment

env2 = KuruveGymEnv(headless=True, observation_size=(128, 128), fps_cap=0, frameskip=20, enable_powerups=False, verbose=1)
obs = env2.reset()
t = 0
for t in range(1000):
    actions = env2.action_space.sample()
    obs, reward, done, info = env2.step(actions)
    if show_obs:
        image = Image.fromarray(obs, "RGB")
        if 10 < t < 12:
            #image.show()
            image.save("img2.bmp")
        t += 1

env2.close()

