from kuruve.envs.SimpleAiEnv import SimpleAiEnv
from PIL import Image
from kuruve.KurveGame import *

import time

"""Testing GymEnvironment and show image of the observation"""

GameConfig.powerup_blacklist = ["gspeed", "gslow", "gthin", "ggod", "rspeed", "rslow", "rthick", "rturn"]
env = SimpleAiEnv(headless=False, observation_size=(96, 96), fps_cap=0, frameskip=15, enable_powerups=False, verbose=1, ai_count=1)

show_obs = True
obs = env.reset()
t = 0
wins = 0
ep = 0
for _ in range(10000):
    actions = env.action_space.sample()
    obs, reward, done, info = env.step(actions)
    #print(Game.clock.get_fps())

    if show_obs:
        #print(obs.shape)
        image = Image.fromarray(obs[..., 0], "L")
        if 15 < t < 17:
            image.show()
            image.save("env_simple_ai.bmp")
            print("img created")
        t += 1
    if done:
        if reward == 1:
            wins += 1
        ep += 1
        env.reset()
print(wins/ep)
env.close()



