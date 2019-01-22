import random

from api.arm_movement import lower_arm, raise_arm
from api.wheel_movement import turn_right, turn_left, move_both_for_seconds
from api.color import get_left_sensor, get_middle_sensor, get_right_sensor, color_to_text
from api.color import get_red, get_blue, get_green, get_yellow, get_white

RED = get_red()
BLUE = get_blue()
GREEN = get_green()
YELLOW = get_yellow()


measurements = {
    RED: (),
    BLUE: ("temperature", "depth", "salinity"),
    GREEN: ("temperature", "salinity")
}

cs_left = get_left_sensor()
cs_middle = get_middle_sensor()
cs_right = get_right_sensor()


lake_measurements = {
    "RED": {},
    "BLUE": {},
    "GREEN": {}
}


def set_measurement(color, measurement):
    global lake_measurements
    lake_measurements[color][measurement[0]] = measurement[1] + " " + measurement[2]


def get_measurements():
    return lake_measurements


def generate_measurement_value(measurement):
    if measurement == "temperature":
        return "temperature", str(round(random.uniform(-70, -50), 3)), "degrees"
    elif measurement == "depth":
        return "depth", str(round(random.uniform(5, 842), 3)), "meters"
    elif measurement == "salinity":
        return "salinity", str(round(random.uniform(0.1, 35), 3)), "per mille"


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
    if color in measurements and len(measurements[color]) != 0:
        position_rover_for_measurement(color)
        lower_arm()
        for measure in measurements[color]:
            text = generate_measurement_value(measure)
            set_measurement(color_to_text(color), text)
            # s.speak(text[0] + text[1] + text[2])
        raise_arm()
