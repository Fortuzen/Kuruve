from kuruve.envs.SimpleAiEnv import SimpleAiEnv
from kuruve.KurveGame import *


"""Testing SimpleAi environment"""

GameConfig.powerup_blacklist = ["gspeed", "gslow", "gthin", "ggod", "rspeed", "rslow", "rthick", "rturn"]
env = SimpleAiEnv(headless=False, observation_size=(96, 96), fps_cap=0, frameskip=10, enable_powerups=True, verbose=1, ai_count=1)

obs = env.reset()
wins = 0
ep = 0
for _ in range(1000):
    actions = env.action_space.sample()
    obs, reward, done, info = env.step(actions)
    if done:
        if reward == 1:
            wins += 1
        ep += 1
        env.reset()
print(wins/ep)
env.close()
