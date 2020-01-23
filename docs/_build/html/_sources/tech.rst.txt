.. _tech:

Technical Notes
==================================
Here are some things about the implementation of the game itself

Game class
----------------------------------
The game class contains the methods to run the game. "init()" must be called before playing the game.

Game config and state
----------------------------------
Game config contains settings that should be set before starting/initializing the game.
Game state contains things that can be changed during the game (eg. screen and collision surface).

Collision detection
----------------------------------
Collision detection is very simple for the worms. One pixel position is taken ahead of the worm and 
then checked against the collision surface. If the color is anything but black, collision happened.

Headless mode
----------------------------------
The game can run without window. The trick is to use environment variables and convert pygame surfaces
to the correct format (on some machines the format of the surface is different).

Powerups
----------------------------------
All powerups inherit the base class Powerup and override handle_collision method. In the handle_collision
method, it is recommended to use event with delays to activate and deactive the powerup effects.

PowerupSpawner spawns powerups on the field if it is activated in the init method of the Game class.
All powerups are added in the init method. These powerups are copied when they are spawned.

Events
----------------------------------
Events can take any function with parameters and triggered after a delay. It should be noted that
events are always triggered on the next tick if delay is 0.
