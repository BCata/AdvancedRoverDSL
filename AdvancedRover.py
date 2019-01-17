#!/usr/bin/env python3

import threading
import random

import functools
from time import sleep
from time import time
from ev3dev2.led import Leds
from ev3dev2.sound import Sound
from ev3dev2._platform.ev3 import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.motor import LargeMotor, MoveTank, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent
from ev3dev2.motor import MediumMotor
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor

import AdvancedRoverBluetooth as arb


SPEED = 30
TIME = 0.4
BORDER_COLOR = ColorSensor.COLOR_WHITE
RED = ColorSensor.COLOR_RED
BLUE = ColorSensor.COLOR_BLUE
YELLOW = ColorSensor.COLOR_YELLOW
GREEN = ColorSensor.COLOR_GREEN

FIND_LAKES_TIMEOUT = 200
GLOBAL_TIMEOUT = 300

# value = 0
lakes_found = False
color_found = {
    RED: False,
    BLUE: False,
    GREEN: False
}

measurements = {
    RED: (),
    BLUE: ("temp","depth","sal"),
    GREEN: ("temp","sal")
}

current_ultrasonic_distance = 0
previous_ultrasonic_distance = 0
bricks_to_push = 1
bricks_pushed = False

s = Sound()
leds = Leds()
cs_left = ColorSensor(INPUT_1)
cs_middle = ColorSensor(INPUT_3)
cs_right = ColorSensor(INPUT_4)
us_back = UltrasonicSensor(INPUT_2)
us_back.mode = 'US-DIST-CM'
arm = MediumMotor(OUTPUT_B)
left_wheel = LargeMotor(OUTPUT_A)
right_wheel = LargeMotor(OUTPUT_D)
both_wheels = MoveTank(OUTPUT_A, OUTPUT_D)

color_sensors = [cs_left, cs_middle, cs_right]


def move_both_for_seconds(percent, seconds, blocking=True):
    both_wheels.on_for_seconds(SpeedPercent(percent),
                                SpeedPercent(percent),
                                seconds,
                                brake=False,
                                block=blocking)


def move_both(percent):
    both_wheels.on(SpeedPercent(percent),
                                SpeedPercent(percent))


def move_back(percent, seconds, blocking=True):
    move_both_for_seconds(-percent, seconds, blocking=blocking)


def turn_left(percent, seconds, blocking=True):
    right_wheel.on_for_seconds(SpeedPercent(percent),
                               seconds, brake=False,
                               block=blocking)


def turn_right(percent, seconds, blocking=True):
    left_wheel.on_for_seconds(SpeedPercent(percent),
                              seconds, brake=False,
                              block=blocking)


def lower_arm():
    arm.on_for_degrees(SpeedPercent(-10), 90)


def raise_arm():
    arm.on_for_degrees(SpeedPercent(10), 90)


def detect_line():
    return cs_left.color == BORDER_COLOR, cs_middle.color == BORDER_COLOR, cs_right.color == BORDER_COLOR


def detect_color():
    return cs_left.color, cs_middle.color, cs_right.color


def collision_protocol2(color_sensor_tuple):
    leds.set_color("LEFT", "RED") 
    leds.set_color("RIGHT", "RED")
    if color_sensor_tuple[0]:
        print("Angle: ", arb.angle) 
        while abs(arb.angle) < 90:
            print("Angle: ", arb.angle) 
            turn_left(-SPEED, TIME)
            turn_right(SPEED,TIME)
        if(abs(arb.angle) >= 90):
            print("Angle: ", arb.angle) 
            both_wheels.off()
            arb.write_to_socket(sock_out, "reset_gyro")

    elif color_sensor_tuple[2]:
        print("Angle: ", arb.angle) 
        while abs(arb.angle) < 90:
            print("Angle: ", arb.angle) 
            turn_right(-SPEED, TIME)
            turn_left(SPEED,TIME)
        if(abs(arb.angle) >= 90):
            print("Angle: ", arb.angle) 
            both_wheels.off()
            arb.write_to_socket(sock_out, "reset_gyro")

    elif color_sensor_tuple[1]:
        move_back(20, 2)

    leds.set_color("LEFT", "GREEN") 
    leds.set_color("RIGHT", "GREEN")


def color_collision_protocol(color_sensor_tuple):
    leds.set_color("LEFT", "RED") 
    leds.set_color("RIGHT", "RED")

    if color_sensor_tuple[0]:
        both_wheels.off()
        move_back(15, TIME)
        turn_left(-30, TIME)
        turn_right(30,TIME)
    elif color_sensor_tuple[2]:
        both_wheels.off()
        move_back(15, TIME)
        turn_right(-30, TIME)
        turn_left(30,TIME)
    elif color_sensor_tuple[1]:
        move_back(15, 2)
        if random.randint(1,2) == 1:
            turn_left(-10, TIME)
            turn_right(10,TIME)
        else:
            turn_right(-10, TIME)
            turn_left(10,TIME)
    if us_back.value()/10 >= 4:
        both_wheels.off()
        sleep(0.5)
        move_both_for_seconds(30, TIME)

    leds.set_color("LEFT", "GREEN") 
    leds.set_color("RIGHT", "GREEN")


def ultrasonic_collision_protocol():
    both_wheels.off()
    leds.set_color("LEFT", "RED")
    leds.set_color("RIGHT", "RED")

    move_back(15, TIME)
    if random.randint(1, 2) == 1:
        turn_left(-30, TIME)
        turn_right(30, TIME)
    else:
        turn_left(30, TIME)
        turn_right(-30, TIME)

    leds.set_color("LEFT", "GREEN")
    leds.set_color("RIGHT", "GREEN")


def touch_collision_protocol(touch_sensor_tuple):
    both_wheels.off()
    move_back(15, TIME)
    if touch_sensor_tuple[0] :
        turn_left(-30, TIME)
        turn_right(30, TIME)
    elif touch_sensor_tuple[1]:
        turn_left(30, TIME)
        turn_right(-30, TIME)


def generate_measurement_value(measurement):
    if measurement == "temp" :
        return "temperature", str(round(random.uniform(-70,-50),3)), "degrees"
    elif measurement == "depth":
        return "depth", str(round(random.uniform(5,842),3)), "meters"
    elif measurement == "sal":
        return "salinity", str(round(random.uniform(0.1, 35),3)), "per mille"


def position_rover_for_measurement(lake_color):
    counter = 0

    while cs_middle.color != lake_color or cs_left.color == lake_color or cs_right.color == lake_color:
        if cs_left.color == lake_color:
            turn_left(10, 0.4)
            turn_right(-10, 0.4)
        elif cs_right.color == lake_color:
            turn_left(-10, 0.4)
            turn_right(10, 0.4)
        else:
            if counter < 4:
                move_both_for_seconds(10, 0.4)
                counter += 1


def measure_lake(color):
    if len(measurements[color]) != 0:
        position_rover_for_measurement(color)
        lower_arm()
        for measure in measurements[color]:
            text = generate_measurement_value(measure)
            # s.speak(text[0] + text[1] + text[2])
        raise_arm()


def process_lake(color_val, color_name):
    s.speak(color_name + "found")
    measure_lake(color_val)
    color_found[color_val] = True

    # set mission as completed if all lakes are found
    global lakes_found
    lakes_found = all(list(color_found.values()))


def detect_lakes(color_sensor_tuple, lakes):
    color_sensor_firing = [False, False, False]
    has_time_elapsed = time() - findLakesStart >= FIND_LAKES_TIMEOUT

    global lakes_found
    if has_time_elapsed:
        lakes_found = True

    for index, color in enumerate(color_sensor_tuple):
        if color in lakes:
            color_sensor_firing[index] = True
            both_wheels.off()
            if color == RED and not color_found[RED] and not has_time_elapsed:
                process_lake(RED, "Red")
            if color == YELLOW and not color_found[YELLOW] and not has_time_elapsed:
                process_lake(YELLOW, "Yellow")
            if color == BLUE and not color_found[BLUE] and not has_time_elapsed:
                process_lake(BLUE, "Blue")
            if color == GREEN and not color_found[GREEN] and not has_time_elapsed:
                process_lake(GREEN, "Green")

    color_collision_protocol(color_sensor_firing)


def mission_ongoing():

    # global timeout exceeded
    if time() - globalStart >= GLOBAL_TIMEOUT:
        return False

    # if all missions completed
    if lakes_found and bricks_pushed:
        return False

    return True


def decode_message():
    return arb.read_message()


def detect_ultrasonic():
    global bricks_to_push, previous_ultrasonic_distance, current_ultrasonic_distance, bricks_pushed

    # detect ultrasonic input from secondary brick
    message = decode_message()

    if bricks_to_push == 0:
        bricks_pushed = True

    if message[0] == "ultrasonic":
        previous_ultrasonic_distance = current_ultrasonic_distance
        current_ultrasonic_distance = message[1]

        if bricks_to_push == 0:
            ultrasonic_collision_protocol()

        arb.set_message(("clear", None))
    else:
        current_ultrasonic_distance = 0

    # if brick has fallen off the edge, decrement counter
    if previous_ultrasonic_distance != 0 and current_ultrasonic_distance == 0:
        bricks_to_push -= 1
        previous_ultrasonic_distance = current_ultrasonic_distance = 0


def detect_touch():
    message = decode_message()
    if message[0] == "touch":
        touch_collision_protocol(message[1])
        arb.set_message(("clear", None))


if __name__ == "__main__":
    sock, sock_in, sock_out = arb.connect()
    listener = threading.Thread(target=arb.listen, args=(sock_in, sock_out, mission_ongoing))
    listener.start()

    lakes_to_find = (RED, GREEN, BLUE)

    # start timers
    globalStart = time()
    findLakesStart = time()

    while mission_ongoing():
        # TODO: implement timeout for pushing bricks
        color_collision_protocol(detect_line())
        detect_lakes(detect_color(), lakes_to_find)
        move_both(SPEED)

        detect_ultrasonic()
        detect_touch()

    both_wheels.off()
    arb.write_to_socket(sock_out, False)
    s.speak("Mission")
