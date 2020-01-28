from kuruve.envs.GymEnv import KuruveGymEnv
from PIL import Image
from kuruve.KurveGame import *

"""Testing GymEnvironment and show image of the observation"""

GameConfig.powerup_blacklist = ["gspeed", "gslow", "gthin", "ggod", "rspeed", "rslow", "rthick", "rturn"]
env = KuruveGymEnv(headless=True, observation_size=(96, 96), fps_cap=0, frameskip=1, enable_powerups=True, verbose=1)

show_obs = True
obs = env.reset()
t = 0
for _ in range(1000):
    actions = env.action_space.sample()
    obs, reward, done, info = env.step(actions)
    if show_obs:
        image = Image.fromarray(obs[0], "RGB")
        if 10 < t < 12:
            #image.show()
            image.save("img.bmp")
        t += 1
env.close()

# Create environment headless environment

env2 = KuruveGymEnv(headless=True, observation_size=(128, 128), fps_cap=0, frameskip=20, enable_powerups=False, verbose=1)
obs = env2.reset()
t = 0
for t in range(1000):
    actions = env2.action_space.sample()
    obs, reward, done, info = env2.step(actions)
    if show_obs:
        image = Image.fromarray(obs[0], "RGB")
        if 10 < t < 12:
            #image.show()
            image.save("img2.bmp")
        t += 1

env2.close()

