import random

import api.rover_bluetooth as arb

from api.color import get_black, get_white
from api.touch import detect_touch
from api.wheel_movement import move_both_in_direction
from api.color import color_collision_protocol, detect_color, detect_line
from api.color import get_right_sensor, get_left_sensor, get_middle_sensor
from api.wheel_movement import move_both, move_back, turn_left, turn_right
from api.ultrasonic import ultrasonic_collision_protocol, ultrasonic_back_collision_protocol, get_ultrasonic_back_value, \
    detect_ultrasonic_front

cs_left = get_left_sensor()
cs_middle = get_middle_sensor()
cs_right = get_right_sensor()

terrain_color = get_black()
border_color = get_white()


def found_parking_spot(color_sensor_tuple):
    return color_sensor_tuple[0] and color_sensor_tuple[2]


def position_on_border_line(border_color):
    last_sensor_fired = "left"
    turn_speed = 5
    while not found_parking_spot(detect_line(border_color)):
        if cs_left.color == border_color:
            turn_right(-turn_speed, 0.1)
            turn_left(turn_speed, 0.2)
            last_sensor_fired = "left"
        elif cs_right.color == border_color:
            turn_left(-turn_speed, 0.1)
            turn_right(turn_speed, 0.2)
            last_sensor_fired = "right"
        elif cs_middle.color == border_color:
            move_back(10, 1)
            if last_sensor_fired == "right":
                turn_left(-10, 0.3)
                turn_right(10, 0.3)
            else:
                turn_right(-10, 0.3)
                turn_left(10, 0.3)
        else:
            move_both(10)


def on_the_border(color_sensor_tuple):
    return color_sensor_tuple[0] or color_sensor_tuple[2] \
           or get_ultrasonic_back_value()/10 > 4


def move_to_border(border_color):
    while not on_the_border(detect_line(border_color)):
        move_both(15)
        # color_collision_protocol(detect_line(border_color))
        color_collision_protocol([get_left_sensor().color != terrain_color and get_left_sensor().color != border_color,
                                  get_middle_sensor().color != terrain_color and get_middle_sensor().color != border_color,
                                  get_right_sensor().color != terrain_color and get_right_sensor().color != border_color])
        ultrasonic_back_collision_protocol()
        # print("Calling ultrasonic front:")
        detect_ultrasonic_front()
        detect_touch()


def turn_90_degrees(direction="random"):
    speed = 12
    time = 1.48
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


def move_to_corner(border_color, direction="forward"):
    while not on_the_border(detect_line(border_color)):
        move_both_in_direction(15, direction)
        cs = detect_color()

        if cs[0] == border_color or cs[1] == border_color or cs[2] == border_color:
            continue

        if arb.read_message()[0] == "ultrasonic" \
                or arb.read_message()[0] == "touch" \
                or (cs[0] != terrain_color or cs[1] != terrain_color or cs[2] != terrain_color):
                    arb.set_message(("clear", None))
                    direction = toggle_direction(direction)
                    move_both_in_direction(15, direction, 1)


def park_rover(border_color):
    move_to_border(border_color)
    position_on_border_line(border_color)
    turn_90_degrees()
    move_to_corner(border_color)
