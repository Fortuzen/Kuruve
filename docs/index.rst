.. Kuruve documentation master file, created by
   sphinx-quickstart on Tue Jan  7 13:07:28 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Kuruve's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   kuruve
   install
   tech
   environments
   examples

Minimal example
----------------------------------

.. code-block:: python

   from kuruve.envs.GymEnv import KuruveGymEnv
   from kuruve.KurveGame import *

   env = KuruveGymEnv(headless=False, observation_size=(96, 96), fps_cap=0, frameskip=1, enable_powerups=False, verbose=0)
   obs = env.reset()
   for _ in range(1000):
       actions = env.action_space.sample()
       obs, reward, done, info = env.step(actions)
   env.close()


.. What is Kuruve
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
