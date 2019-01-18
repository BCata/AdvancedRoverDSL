from api.wheel_movement import stop_both, move_back, turn_right, turn_left

TIME = 0.4


def touch_collision_protocol(touch_sensor_tuple):
    stop_both()
    move_back(15, TIME)
    if touch_sensor_tuple[0]:
        turn_left(-30, TIME)
        turn_right(30, TIME)
    elif touch_sensor_tuple[1]:
        turn_left(30, TIME)
        turn_right(-30, TIME)
