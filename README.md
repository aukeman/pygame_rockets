pygame_rockets
==============

multiplayer "asteroids"-derived game written using pygame 

![screenshot 1](https://github.com/aukeman/pygame_rockets/blob/master/screenshot_1.png?raw=true "screenshot 1")

Usage:
------

    pygame_rockets.py -h | [-f] [-S] [-b] [-s] [-p] [-t] [-o] [-a <number of asteroids>] [-1 arrows|wads|joystick] [-2 arrows|wads|joystick]
    
    -h   this message
    -f   fullscreen
    -S   disable open gl shaders
    -b   draw bounding boxes
    -s   suppress drawing starfield
    -p   suppress drawing planets
    -t   draw toon shading outlines
    -o   one player only
    -a   initial number of asteroids (defaults to 1)
    -1   controls for player one (defaults to arrow keys/spacebar)
    -2   controls for player two (defaults to WADS keys/left ctrl)

![screenshot 2](https://github.com/aukeman/pygame_rockets/blob/master/screenshot_2.png?raw=true "screenshot 2")

Controls:
---------

### arrow keys:
-  Rotate Left: left arrow
-  Rotate Right: right arrow
-  Thrust: up arrow
-  Tractor beam: down arrow
-  Fire: spacebar

### WADS keys:
-  Rotate Left: a
-  Rotate Right: d
-  Thrust: w
-  Tractor beam: s
-  Fire: left control

### Joystick:
-  Rotate Left: joystick left
-  Rotate Right: joystick right
-  Thrust: joystick up
-  Tractor beam: 2nd stick (I wrote this using a gamepad with two analogue sticks)
-  Fire: fire button

TODOs:
------
-  when running fullscreen, the game won't detect when you're trying to quit (escape), and you have to kill the process
-  rendering is pretty slow.  on a beefy video card it works ok, but the frame rate really drops on anything else.  I'm sure the opengl code could be tightened up quite a bit.  In the meantime, it helps to suppress drawing the planets in the background.
-  the joystick assumes a gamepad with two analogue sticks. should probably account for regular 2-axis joysticks
-  the tractor beam doesn't do anything.  but at least it looks cool
-  asteroid/ship collision detection isn't too great
-  need to add some sort of goal :)
