import sys

from controls import JoystickControl, KeyboardControl, ARROWS, WADS
from getopt import getopt

_arrows_controls=KeyboardControl(ARROWS)
_wads_controls=KeyboardControl(WADS)
_joystick_controls=JoystickControl() 

fullscreen = False
    
draw_bounding_boxes = False
draw_planets = True
draw_starfield = True
draw_toon_shading_outlines = False

initial_number_of_asteroids = 1

enable_player_2 = True

player_1_control = _arrows_controls
player_2_control = _wads_controls

def load_from_command_line():

    global fullscreen
    global draw_bounding_boxes
    global draw_planets
    global draw_starfield
    global draw_toon_shading_outlines
    global initial_number_of_asteroids
    global enable_player_2
    global player_1_control
    global player_2_control
	
    (opts,args) = getopt(sys.argv[1:], "hfsbptoa:1:2:") 

    for flag,value in opts:

        if flag=="-h":
            print _usage_string()
            sys.exit(0)
            
        elif flag=="-f":
            fullscreen=True

        elif flag=="-s":
            draw_starfield=False

        elif flag=="-b":
            draw_bounding_boxes=True

        elif flag=="-p":
            draw_planets=False            

        elif flag=="-t": 
            draw_toon_shading_outlines=True

        elif flag=="-o":
            enable_player_2=False

        elif flag=="-a":
            initial_number_of_asteroids = int(value)
            
        elif flag=="-1":
            player_1_control=_get_control(value)

            if player_1_control is None:
                print >>sys.stderr, "unable to configure controls for player 1"
                sys.exit(1)
            
        elif flag=="-2":
            player_2_control=_get_control(value)
        
            if player_2_control is None:
                print >>sys.stderr, "unable to configure controls for player 2"
                sys.exit(1)

def _usage_string():
    return """Usage:
%s -h | [-f] [-b] [-s] [-p] [-t] [-o] [-a <number of asteroids>] [-1 arrows|wads|joystick] [-2 arrows|wads|joystick]
    
-h   this message
-f   fullscreen
-b   draw bounding boxes
-s   suppress drawing starfield
-p   suppress drawing planets
-t   draw toon shading outlines
-o   one player only
-a   initial number of asteroids (defaults to 1)
-1   controls for player one (defaults to arrow keys/spacebar)
-2   controls for player two (defaults to WADS keys/left ctrl) 
""" % sys.argv[0]


def _get_control( control_type_string ):

    result=None

    if control_type_string=="arrows":
        result=_arrows_controls

    elif control_type_string=="wads":
        result=_wads_controls

    elif control_type_string=="joystick":
     
        if _joystick_controls.is_valid():
            result=_joystick_controls
        else:
            print >>sys.stderr, "Joystick is not configured"
    else:
            print >>sys.stderr, "unknown control type (\"%s\")" % value

    return result