import api.rover_bluetooth as arb
from api.wheel_movement import stop_both, move_back, turn_right, turn_left


TIME = 0.4

touch_encountered = False


def get_touch_encountered():
    return touch_encountered


def set_touch_encountered(value):
    global touch_encountered
    touch_encountered = value


def touch_collision_protocol(touch_sensor_tuple):
    stop_both()
    move_back(15, TIME)
    if touch_sensor_tuple[0]:
        turn_left(30, TIME)
        turn_right(-30, TIME)
    elif touch_sensor_tuple[1]:
        turn_left(-30, TIME)
        turn_right(30, TIME)


def detect_touch():
    global touch_encountered
    message = arb.read_message()

    if message[0] == "touch":
        touch_encountered = True
        touch_collision_protocol(message[1])
        arb.set_message(("clear", None))

