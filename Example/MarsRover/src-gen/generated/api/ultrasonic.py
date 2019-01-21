import random

import api.rover_bluetooth as arb

from time import sleep
from ev3dev2.led import Leds
from ev3dev2._platform.ev3 import INPUT_2
from ev3dev2.sensor.lego import UltrasonicSensor
from api.wheel_movement import stop_both, move_back, turn_right, turn_left
from api.wheel_movement import move_both_for_seconds


leds = Leds()
TIME = 0.4

us_back = UltrasonicSensor(INPUT_2)
us_back.mode = 'US-DIST-CM'


def ultrasonic_collision_protocol():
    stop_both()
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


def ultrasonic_back_collision_protocol():
    if us_back.value()/10 >= 4:
        stop_both()
        sleep(0.4)
        move_both_for_seconds(30, TIME)


def detect_ultrasonic_front():
    if arb.read_message()[0] == "ultrasonic":
        # print("Received ultrasonic")
        ultrasonic_collision_protocol()
        arb.set_message(("clear", None))


def get_ultrasonic_back_value():
    return us_back.value()

