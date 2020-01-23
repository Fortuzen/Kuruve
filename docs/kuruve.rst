.. _kuruve:

Kuruve
==================================

What is Kuruve
----------------------------------

Kuruve is "Achtung, die Kurve!/Curve Fever" clone and learning environment.
The goal of the game is to be the last worm standing in the field. You have to avoid other worms and use powerups 
to your advantage.

There is also a "survival" game mode in which you try to avoid white areas as long as possible.

* `Wikipedia <https://en.wikipedia.org/wiki/Achtung,_die_Kurve!>`_ 
* `Kurve (flash) <http://www.crazygames.com/game/achtung-die-kurve>`_
* `Kurve (DOS) <https://www.retrogames.cz/play_1285-DOS.php>`_

How to play
-------------
Run main.py to play the game normally against other (human) players.

Controls are very simple: just left and right turn.
Default controls (turn left, turn right) are:

* Player 1: left arrow, right arrow
* Player 2: a, s
* Player 3: v, b
* Player 4: k, l

Avoid other players or try to flank them and lead them to a dead-end.
Powerups might be useful or harmful depending on the situation.


Powerups
-------------
There are currently 9 powerups. Each powerup is colored and marked by a letter.
Green powerups affect only you. Red powerups affect others. Blue powerups affect everyone.
Note: For the time being, it is not recommended to use powerups in learning experiments.

Green powerups
^^^^^^^^^^^^^^
* Speed (A) - Move faster
* Slow (D) - Move slower
* God (G) - Cannot die for a moment
* Thin (B) - Smaller head

Red powerups
^^^^^^^^^^^^^^
* Speed (A) - Others move faster
* Slow (D) - Others move slower
* Turn90 (T) - Others can only make 90 degree turns
* Thick (B) - Others have bigger heads

Blue powerups
^^^^^^^^^^^^^^
* Eraser (R) - Reset the field (remove all lines)

Gameconfig
--------------
You change these values before initializing the game.

.. module:: kuruve.GameConfig
.. autoclass:: GameConfig
   :members:
