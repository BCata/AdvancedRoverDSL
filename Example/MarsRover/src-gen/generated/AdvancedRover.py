#!/usr/bin/env python3
import sys
import threading
from math import floor

from time import time
from ev3dev2.sound import Sound

import api.rover_bluetooth as arb
from api.celebration import celebrate
from api.mission_report import generate_mission_report

from api.touch import detect_touch, get_touch_encountered, set_touch_encountered
from api.parking import park_rover
from api.measurements import measure_lake, get_measurements
from api.wheel_movement import move_both, stop_both, move_both_for_seconds
from api.color import color_collision_protocol, detect_color, detect_line
from api.color import get_right_sensor, get_left_sensor, get_middle_sensor
from api.color import get_red, get_blue, get_green, get_yellow, get_white, get_black
from api.ultrasonic import ultrasonic_collision_protocol, ultrasonic_back_collision_protocol

BORDER_COLOR = get_white()
BLACK = get_black()
BLUE = get_blue()
RED = get_red()
GREEN = get_green()

color_found = {
	BLUE = False,
	RED = False,
	GREEN = False
}

GLOBAL_TIMEOUT = 300

FIND_LAKES_TIMEOUT = 100
lakes_found = False

PUSH_BRICKS_TIMEOUT = 100
initial_number_of_bircks = 2
bricks_pushed = False
bricks_to_push = initial_number_of_bricks


s = Sound()
cs_left = get_left_sensor()
cs_middle = get_middle_sensor()
cs_right = get_right_sensor()


def create_mission_report():
    timeouts = {'global_timeout': GLOBAL_TIMEOUT,
                'global_time_elapsed': mission_duration,
                'find_lakes_timeout': FIND_LAKES_TIMEOUT,
                'find_lakes_elapsed_time': min(find_lakes_duration, mission_duration),
                'push_bricks_timeout': PUSH_BRICKS_TIMEOUT,
                'push_bricks_elapsed_time': min(push_bricks_duration, mission_duration)
                }

    measurements = {'lakes': get_measurements(),
                    'bricks_pushed': "{0} out of {1}".format(initial_number_of_bricks - bricks_to_push,
                                                             initial_number_of_bricks),
                    'celebrate': 'sing'
                    }

    generate_mission_report(timeouts, measurements)
