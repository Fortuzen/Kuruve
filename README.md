# Kuruve
Python/PyGame Curve Fever clone and learning environment

You should head to the documentation to learn more about this environment.

[Kuruve Documentation](https://kuruve.readthedocs.io/en/latest/index.html)

### Minimal example
```
from kuruve.envs.GymEnv import KuruveGymEnv
from kuruve.KurveGame import *

env = KuruveGymEnv(headless=False, observation_size=(96, 96), fps_cap=0, frameskip=1, enable_powerups=False, verbose=0)
obs = env.reset()
for _ in range(1000):
    actions = env.action_space.sample()
    obs, reward, done, info = env.step(actions)
env.close()
```

### Future work
* Port to cython or c++ for more fps.
* Powerup observations for environments.
* Actual GUI for real players. Like main menu.


