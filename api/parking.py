import random

import api.rover_bluetooth as arb

from api.color import get_black
from api.touch import detect_touch
from api.wheel_movement import move_both_in_direction
from api.color import color_collision_protocol, detect_color, detect_line
from api.color import get_right_sensor, get_left_sensor, get_middle_sensor
from api.wheel_movement import move_both, move_back, turn_left, turn_right
from api.ultrasonic import ultrasonic_collision_protocol, ultrasonic_back_collision_protocol, get_ultrasonic_back_value

cs_left = get_left_sensor()
cs_middle = get_middle_sensor()
cs_right = get_right_sensor()

BLACK = get_black()


def found_parking_spot(color_sensor_tuple):
    print("Left: ", color_sensor_tuple[0])
    print("Right: ", color_sensor_tuple[2])
    return color_sensor_tuple[0] and color_sensor_tuple[2]


def position_on_border_line(border_color):
    last_sensor_fired = "left"
    while not found_parking_spot(detect_line(border_color)):
        if cs_left.color == border_color:
            turn_right(-5, 0.1)
            turn_left(5, 0.2)
            last_sensor_fired = "left"
        elif cs_right.color == border_color:
            turn_left(-5, 0.1)
            turn_right(5, 0.2)
            last_sensor_fired = "right"
        elif cs_middle.color == border_color:
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


def move_to_border(border_color):
    while not on_the_border(detect_line(border_color)):
        move_both(15)
        color_collision_protocol(detect_line(border_color))
        ultrasonic_back_collision_protocol()
        ultrasonic_collision_protocol()
        detect_touch()


def turn_90_degrees(direction="random"):
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
        # push_bricks()
        # detect_touch()
        cs = detect_color()
        if arb.read_message()[0] == "ultrasonic" \
                or arb.read_message()[0] == "touch" \
                or cs[0] != BLACK or cs[1] != BLACK or cs[2] != BLACK:
                    direction = toggle_direction(direction)
                    move_both_in_direction(15, direction, 1)


def park_rover(border_color):
    move_to_border(border_color)
    position_on_border_line(border_color)
    turn_90_degrees()
    move_to_corner()
