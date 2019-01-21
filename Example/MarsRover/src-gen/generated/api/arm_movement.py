from ev3dev2.motor import MediumMotor, OUTPUT_B, SpeedPercent

arm = MediumMotor(OUTPUT_B)


def lower_arm():
    arm.on_for_degrees(SpeedPercent(-10), 100)


def raise_arm():
    arm.on_for_degrees(SpeedPercent(10), 100)

