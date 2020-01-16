"""
Testing GymEnvironment
"""

from GymEnv import KuruveGymEnv

from PIL import Image

from GameConfig import GameConfig


GameConfig.powerup_blacklist = ["gspeed", "gslow", "gthin", "ggod", "rspeed", "rslow", "rthick", "rturn"]
env = KuruveGymEnv(headless=False, observation_size=(96, 96), fps_cap=0, frameskip=10, enable_powerups=True, verbose=1)

show_obs = False
obs = env.reset()
t = 0
for _ in range(1000):
    actions = env.action_space.sample()
    obs, reward, done, info = env.step(actions)

    if show_obs:
        #image = Image.frombuffer("RGB", (128, 128), obs[0], "raw", "RGB", 0, 1)
        image = Image.fromarray(obs[0], "RGB")
        #image = Image.fromarray(obs[0], "L")
        if t > 5 and t < 10:
            image.convert("L").show()
        t += 1

    if done:
        print("Terminal")
        obs = env.reset()
env.close()

# Create environment again

env2 = KuruveGymEnv(headless=True, observation_size=(128, 128), fps_cap=0, frameskip=20, enable_powerups=False, verbose=1)
obs = env2.reset()
for t in range(1000):
    actions = env2.action_space.sample()
    obs, reward, done, info = env2.step(actions)
    if done:
        print("Terminal")

env2.close()

