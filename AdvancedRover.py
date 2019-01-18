#!/usr/bin/env python3

import threading
import random

from time import time
from ev3dev2.sound import Sound

import AdvancedRoverBluetooth as arb

from api.wheel_movement import move_both, stop_both, move_back, turn_left, turn_right
from api.ultrasonic import ultrasonic_collision_protocol, ultrasonic_back_collision_protocol
from api.color import color_collision_protocol, detect_color, detect_line
from api.color import get_right_sensor, get_left_sensor, get_middle_sensor
from api.color import get_red, get_blue, get_green, get_yellow, get_white
from api.measurements import measure_lake
from api.touch import detect_touch

SPEED = 30
BORDER_COLOR = get_white()
RED = get_red()
BLUE = get_blue()
GREEN = get_green()
YELLOW = get_yellow()

GLOBAL_TIMEOUT = 2
FIND_LAKES_TIMEOUT = 200
PUSH_BRICKS_TIMEOUT = 10

# value = 0
lakes_found = False
color_found = {
    RED: False,
    BLUE: False,
    GREEN: False
}

bricks_pushed = False
current_ultrasonic_distance = 0
previous_ultrasonic_distance = 0
bricks_to_push = 2

s = Sound()
cs_left = get_left_sensor()
cs_middle = get_middle_sensor()
cs_right = get_right_sensor()


def process_lake(color_val, color_name):
    s.speak(color_name + "found")
    measure_lake(color_val)
    color_found[color_val] = True

    # set mission as completed if all lakes are found
    global lakes_found
    lakes_found = all(list(color_found.values()))


def detect_lakes(color_sensor_tuple, lakes):
    color_sensor_firing = [False, False, False]
    has_time_elapsed = time() - globalStart >= FIND_LAKES_TIMEOUT

    global lakes_found
    if has_time_elapsed:
        lakes_found = True

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

    # global timeout exceeded
    if time() - globalStart >= GLOBAL_TIMEOUT:
        return False

    # if all missions completed
    if lakes_found and bricks_pushed:
        return False

    return True


def detect_ultrasonic():
    global bricks_to_push, previous_ultrasonic_distance, current_ultrasonic_distance, bricks_pushed
    has_time_elapsed = time() - globalStart >= PUSH_BRICKS_TIMEOUT

    # detect ultrasonic input from secondary brick
    message = arb.read_message()

    if message[0] == "ultrasonic":

        if bricks_to_push == 0 or has_time_elapsed:
            # done pushing bricks
            bricks_pushed = True
            ultrasonic_collision_protocol()
        else:
            # prepare decrement number of bricks after brick falls
            previous_ultrasonic_distance = current_ultrasonic_distance
            current_ultrasonic_distance = message[1]

        arb.set_message(("clear", None))
    else:
        current_ultrasonic_distance = 0

    # if brick has fallen off the edge, decrement counter
    if bricks_to_push > 0 and previous_ultrasonic_distance != 0 and current_ultrasonic_distance == 0:
        bricks_to_push -= 1
        previous_ultrasonic_distance = current_ultrasonic_distance = 0


def found_parking_spot(color_sensor_tuple):
    print("Left: ", color_sensor_tuple[0])
    print("Right: ", color_sensor_tuple[2])
    return color_sensor_tuple[0] and color_sensor_tuple[2]


def position_on_border_line():
    while not found_parking_spot(detect_line(BORDER_COLOR)):
        if cs_left.color == BORDER_COLOR:
            # if random.randint(1, 2) == 1:
            turn_right(-5, 0.1)
            # else:
            turn_left(5, 0.2)
        elif cs_right.color == BORDER_COLOR:
            # if random.randint(1, 2) == 1:
            turn_left(-5, 0.1)
            # else:
            turn_right(5, 0.2)
        elif cs_middle.color == BORDER_COLOR:
            move_back(10, 1)
            if random.randint(1, 2) == 1:
                turn_left(-10, 0.3)
                turn_right(10, 0.3)
            else:
                turn_right(-10, 0.3)
                turn_left(10, 0.3)
        else:
            move_both(15)


def on_the_border(color_sensor_tuple):
    return color_sensor_tuple[0] or color_sensor_tuple[1] or color_sensor_tuple[2]


def move_to_border():
    while not on_the_border(detect_line(BORDER_COLOR)):
        move_both(SPEED)
        color_collision_protocol(detect_line(BORDER_COLOR))
        ultrasonic_back_collision_protocol()
        detect_ultrasonic()
        detect_touch()


def turn_90_degrees():
    pass


def move_to_corner():
    pass


if __name__ == "__main__":
    sock, sock_in, sock_out = arb.connect()
    listener = threading.Thread(target=arb.listen, args=(sock_in, sock_out, mission_ongoing))
    listener.start()

    lakes_to_find = (RED, GREEN, BLUE)

    # start timers
    globalStart = time()

    while mission_ongoing():
        color_collision_protocol(detect_line(BORDER_COLOR))
        ultrasonic_back_collision_protocol()
        detect_lakes(detect_color(), lakes_to_find)
        move_both(SPEED)

        detect_ultrasonic()
        detect_touch()

    # park rover
    move_to_border()
    position_on_border_line()
    turn_90_degrees()
    move_to_corner()

    stop_both()
    arb.write_to_socket(sock_out, False)
    s.speak("Mission")
