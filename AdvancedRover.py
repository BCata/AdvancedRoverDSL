#!/usr/bin/env python3

import threading
import random

from time import time
from ev3dev2.sound import Sound

import AdvancedRoverBluetooth as arb

from api.wheel_movement import move_both, stop_both, move_back, turn_left, turn_right, move_both_for_seconds
from api.ultrasonic import ultrasonic_collision_protocol, ultrasonic_back_collision_protocol, get_ultrasonic_back_value
from api.color import color_collision_protocol, detect_color, detect_line
from api.color import get_right_sensor, get_left_sensor, get_middle_sensor
from api.color import get_red, get_blue, get_green, get_yellow, get_white, get_black
from api.measurements import measure_lake
from api.touch import detect_touch

SPEED = 30
BORDER_COLOR = get_white()
RED = get_red()
BLUE = get_blue()
GREEN = get_green()
YELLOW = get_yellow()
BLACK = get_black()

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
    last_sensor_fired = "left"
    while not found_parking_spot(detect_line(BORDER_COLOR)):
        if cs_left.color == BORDER_COLOR:
            turn_right(-5, 0.1)
            turn_left(5, 0.2)
            last_sensor_fired = "left"
        elif cs_right.color == BORDER_COLOR:
            turn_left(-5, 0.1)
            turn_right(5, 0.2)
            last_sensor_fired = "right"
        elif cs_middle.color == BORDER_COLOR:
            move_back(10, 1)
            if last_sensor_fired == "left":
                turn_left(-10, 0.3)
                turn_right(10, 0.3)
            else:
                turn_right(-10, 0.3)
                turn_left(10, 0.3)
        else:
            move_both(10)


def on_the_border(color_sensor_tuple):
    return color_sensor_tuple[0] or color_sensor_tuple[1] or color_sensor_tuple[2] \
           or get_ultrasonic_back_value()/10 > 4


def move_to_border():
    while not on_the_border(detect_line(BORDER_COLOR)):
        move_both(15)
        color_collision_protocol(detect_line(BORDER_COLOR))
        ultrasonic_back_collision_protocol()
        detect_ultrasonic()
        detect_touch()


def turn_90_degrees(direction = "random"):
    speed = 15
    time = 1.1
    if direction == "left":
        turn_left(-speed, time)
        turn_right(speed, time)
    elif direction == "right":
        turn_right(-speed, time)
        turn_left(speed, time)
    else:
        if random.randint(1, 2) == 1:
            turn_left(-speed, time)
            turn_right(speed, time)
        else:
            turn_right(-speed, time)
            turn_left(speed, time)


def toggle_direction(direction):
    if direction == "forward":
        return "backwards"
    if direction == "backwards":
        return "forward"


def move_to_corner(direction="forward"):
    while not on_the_border(detect_line()):
        move_both_in_direction(15, direction)
        # color_collision_protocol(detect_line())
        # detect_ultrasonic()
        # detect_touch()
        cs = detect_color()
        if arb.read_message()[0] == "ultrasonic" \
                or arb.read_message()[0] == "touch" \
                or cs[0] != BLACK or cs[1] != BLACK or cs[2] != BLACK:
                    direction = toggle_direction(direction)
                    move_both_in_direction(15, direction, 1)


def move_both_in_direction(percent, direction, seconds=None):
    if seconds:
        if direction == "forward":
            move_both_for_seconds(percent, seconds)
        else:
            move_both_for_seconds(-percent, seconds)
    else:
        if direction == "forward":
            move_both(percent)
        else:
            move_both(-percent)


def park_rover():
    move_to_border()
    position_on_border_line()
    turn_90_degrees()
    move_to_corner()


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

    # mission completed (or timeout exceeded)
    stop_both()
    arb.write_to_socket(sock_out, False)
    s.speak("Mission")

    s.speak("Now let me park")
    park_rover()
    stop_both()
    s.speak("Bye bye")
