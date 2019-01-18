from ev3dev2.motor import LargeMotor, MoveTank, OUTPUT_A, OUTPUT_D, SpeedPercent

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


def stop_both():
    both_wheels.off()


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