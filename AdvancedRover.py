#!/usr/bin/env python3

import bluetooth, threading

from ev3dev2.led import Leds
from ev3dev2.sound import Sound
from ev3dev2._platform.ev3 import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.motor import LargeMotor, MoveTank, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent
from ev3dev2.motor import MediumMotor
from ev3dev2.sensor.lego import TouchSensor, ColorSensor, UltrasonicSensor

SPEED = 30
TIME = 0.4
BORDER_COLOR = ColorSensor.COLOR_WHITE

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
    return (cs_left.color == BORDER_COLOR, cs_middle.color == BORDER_COLOR, cs_right.color == BORDER_COLOR)
        
def collision_protocol(color_sensor_tuple):
    leds.set_color("LEFT", "RED") 
    leds.set_color("RIGHT", "RED")
    if color_sensor_tuple[0]:
        move_back(20, TIME)
        turn_right(SPEED,TIME)

    elif color_sensor_tuple[2]:
        move_back(20, TIME)
        turn_left(SPEED,TIME)

    elif color_sensor_tuple[1]:
        move_back(20, TIME)

def listen_us_back():
    while True:
        if us_back.value()/10 >= 4 :
            both_wheels.off()
    

if __name__ == "__main__":
    back_us_thread = threading.Thread(target=listen_us_back)
    back_us_thread.setDaemon(True)
    back_us_thread.start()

    while True:
        collision_protocol(detect_line())
        move_both(SPEED)
    
