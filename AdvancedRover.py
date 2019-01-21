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

SPEED = 30

BORDER_COLOR = get_white()
RED = get_red()
BLUE = get_blue()
GREEN = get_green()
YELLOW = get_yellow()
BLACK = get_black()

GLOBAL_TIMEOUT = 300
FIND_LAKES_TIMEOUT = 200
PUSH_BRICKS_TIMEOUT = 1

# value = 0
lakes_found = False
color_found = {
    RED: False,
    BLUE: False,
    GREEN: False
}

bricks_pushed = False
initial_number_of_bricks = 1
bricks_to_push = initial_number_of_bricks

s = Sound()
cs_left = get_left_sensor()
cs_middle = get_middle_sensor()
cs_right = get_right_sensor()


def process_lake(color_val, color_name):
    s.speak(color_name + "found")
    measure_lake(color_val)
    color_found[color_val] = True

    # set mission as completed if all lakes are found
    global lakes_found, find_lakes_duration
    lakes_found = all(list(color_found.values()))

    if lakes_found:
        find_lakes_duration = floor(time() - globalStart)


def detect_lakes(color_sensor_tuple, lakes):
    color_sensor_firing = [False, False, False]
    has_time_elapsed = time() - globalStart >= FIND_LAKES_TIMEOUT

    global lakes_found, find_lakes_duration
    if has_time_elapsed:
        lakes_found = True
        find_lakes_duration = floor(time() - globalStart)

    for index, color in enumerate(color_sensor_tuple):
        if color in lakes:
            color_sensor_firing[index] = True
            stop_both()
            if color == RED and not color_found[RED] and not has_time_elapsed:
                process_lake(RED, "Red")
            if color == YELLOW and not color_found[YELLOW] and not has_time_elapsed:
                process_lake(YELLOW, "Yellow")
            if color == BLUE and not color_found[BLUE] and not has_time_elapsed:
                process_lake(BLUE, "Blue")
            if color == GREEN and not color_found[GREEN] and not has_time_elapsed:
                process_lake(GREEN, "Green")

    color_collision_protocol(color_sensor_firing)
    ultrasonic_back_collision_protocol()


def mission_ongoing():
    global mission_duration

    # global timeout exceeded
    if time() - globalStart >= GLOBAL_TIMEOUT:
        mission_duration = floor(time() - globalStart)
        return False

    # if all missions completed
    if lakes_found and bricks_pushed:
        mission_duration = floor(time() - globalStart)
        return False

    return True


current_ultrasonic_distance = 0
previous_ultrasonic_distance = 0


def push_bricks():
    global bricks_to_push, bricks_pushed, previous_ultrasonic_distance, current_ultrasonic_distance, push_bricks_duration

    has_time_elapsed = time() - globalStart >= PUSH_BRICKS_TIMEOUT

    if bricks_to_push == 0 or has_time_elapsed:
        # done pushing bricks
        bricks_pushed = True
        push_bricks_duration = floor(time() - globalStart)

    # detect ultrasonic input from secondary brick
    message = arb.read_message()

    if message[0] == "ultrasonic":
        if bricks_to_push == 0 or has_time_elapsed:
            # done pushing bricks
            ultrasonic_collision_protocol()
        else:
            # prepare decrement number of bricks after brick falls
            previous_ultrasonic_distance = current_ultrasonic_distance
            current_ultrasonic_distance = message[1]

        arb.set_message(("clear", None))
    else:
        current_ultrasonic_distance = 0

    # if brick has fallen off the edge, decrement counter
    if get_touch_encountered():
        set_touch_encountered(False)
    else:
        if bricks_to_push > 0 and previous_ultrasonic_distance != 0 and current_ultrasonic_distance == 0:
            bricks_to_push -= 1
            previous_ultrasonic_distance = current_ultrasonic_distance = 0


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


if __name__ == "__main__":
    sock, sock_in, sock_out = arb.connect()
    listener = threading.Thread(target=arb.listen, args=(sock_in, sock_out, mission_ongoing))
    listener.start()

    lakes_to_find = (RED, GREEN, BLUE)

    mission_duration = sys.maxsize
    find_lakes_duration = sys.maxsize
    push_bricks_duration = sys.maxsize

    # start timers
    globalStart = time()

    while mission_ongoing():
        color_collision_protocol(detect_line(BORDER_COLOR))
        ultrasonic_back_collision_protocol()
        detect_lakes(detect_color(), lakes_to_find)
        move_both(SPEED)
        push_bricks()
        detect_touch()

    # mission completed (or timeout exceeded)
    stop_both()
    s.speak("Exploration finished")

    s.speak("Let us celebrate")
    celebrate("sing")

    s.speak("Now let me park")
    park_rover(BORDER_COLOR)
    stop_both()

    create_mission_report()
    s.speak("Mission report generated")

    s.speak("Mission")
    arb.write_to_socket(sock_out, False)
