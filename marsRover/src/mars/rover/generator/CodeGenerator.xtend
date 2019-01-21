package mars.rover.generator

import mars.rover.dSL.Mission

class CodeGenerator {
	def static toMainCode(Mission root) '''
	'''
	
	def static toSecondaryCode(Mission root) '''
	'''
	
	def static toAPI_armMovement()'''
	from ev3dev2.motor import MediumMotor, OUTPUT_B, SpeedPercent
	
	arm = MediumMotor(OUTPUT_B)
	
	
	def lower_arm():
	    arm.on_for_degrees(SpeedPercent(-10), 100)
	
	
	def raise_arm():
	    arm.on_for_degrees(SpeedPercent(10), 100)
	'''
	def static toAPI_celebration()'''
	from api.wheel_movement import move_both_for_seconds
	from ev3dev2.sound import Sound
	
	s = Sound()
	
	
	def celebrate(celebration="sing"):
	    if celebration == "sing":
	        s.play('resources/celebration_song.wav')
	    elif celebration == "spin":
	        print("spin")
	        move_both_for_seconds(30, 2.3, True, -30)
	'''
	def static toAPI_color()'''
	import random
	
	from ev3dev2.led import Leds
	from ev3dev2.sensor.lego import ColorSensor
	from ev3dev2._platform.ev3 import INPUT_1, INPUT_3, INPUT_4
	from api.wheel_movement import stop_both, move_back, turn_right, turn_left
	
	leds = Leds()
	TIME = 0.4
	
	cs_left = ColorSensor(INPUT_1)
	cs_middle = ColorSensor(INPUT_3)
	cs_right = ColorSensor(INPUT_4)
	
	
	def get_red():
	    return ColorSensor.COLOR_RED
	
	
	def get_blue():
	    return ColorSensor.COLOR_BLUE
	
	
	def get_green():
	    return ColorSensor.COLOR_GREEN
	
	
	def get_yellow():
	    return ColorSensor.COLOR_YELLOW
	
	
	def get_white():
	    return ColorSensor.COLOR_WHITE
	
	
	def get_black():
	    return ColorSensor.COLOR_BLACK
	
	
	def get_left_sensor():
	    return cs_left
	
	
	def get_middle_sensor():
	    return cs_middle
	
	
	def get_right_sensor():
	    return cs_right
	
	
	def color_collision_protocol(color_sensor_tuple):
	    leds.set_color("LEFT", "RED")
	    leds.set_color("RIGHT", "RED")
	
	    if color_sensor_tuple[0]:
	        stop_both()
	        move_back(15, TIME)
	        turn_left(-30, TIME)
	        turn_right(30, TIME)
	    elif color_sensor_tuple[2]:
	        stop_both()
	        move_back(15, TIME)
	        turn_right(-30, TIME)
	        turn_left(30, TIME)
	    elif color_sensor_tuple[1]:
	        move_back(15, 1)
	        if random.randint(1, 2) == 1:
	            turn_left(-10, TIME)
	            turn_right(10, TIME)
	        else:
	            turn_right(-10, TIME)
	            turn_left(10, TIME)
	
	    leds.set_color("LEFT", "GREEN")
	    leds.set_color("RIGHT", "GREEN")
	
	
	def detect_color():
	    return cs_left.color, cs_middle.color, cs_right.color
	
	
	def detect_line(border_color):
	    return cs_left.color == border_color, cs_middle.color == border_color, cs_right.color == border_color
	
	'''
	def static toAPI_measurements()'''
	import random
	
	from api.arm_movement import lower_arm, raise_arm
	from api.wheel_movement import turn_right, turn_left, move_both_for_seconds
	from api.color import get_left_sensor, get_middle_sensor, get_right_sensor
	from api.color import get_red, get_blue, get_green, get_yellow, get_white
	
	RED = get_red()
	BLUE = get_blue()
	GREEN = get_green()
	YELLOW = get_yellow()
	
	
	measurements = {
	    RED: (),
	    BLUE: ("temp", "depth", "sal"),
	    GREEN: ("temp", "sal")
	}
	
	cs_left = get_left_sensor()
	cs_middle = get_middle_sensor()
	cs_right = get_right_sensor()
	
	
	def generate_measurement_value(measurement):
	    if measurement == "temp" :
	        return "temperature", str(round(random.uniform(-70, -50), 3)), "degrees"
	    elif measurement == "depth":
	        return "depth", str(round(random.uniform(5, 842), 3)), "meters"
	    elif measurement == "sal":
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
	    if len(measurements[color]) != 0:
	        position_rover_for_measurement(color)
	        lower_arm()
	        for measure in measurements[color]:
	            text = generate_measurement_value(measure)
	            # s.speak(text[0] + text[1] + text[2])
	        raise_arm()
	
	'''
	def static toAPI_missionReport()'''
	mission_name = "Exploration"
	
	
	def task_finish_cause(timeout, elapsed_time):
	    if elapsed_time >= timeout:
	        return "TIMEOUT EXCEEDED"
	    return "SUCCESS"
	
	
	def report_header(timeout, elapsed_time):
	    report = \'\'\'
	    Mission {0} finished in {1} seconds with {2}
	    \'\'\'.format(mission_name,
	               elapsed_time,
	               task_finish_cause(timeout, elapsed_time))
	
	    return report
	
	
	def lakes_mission_report(timeout, elapsed_time, measurements):
	    measurements_report = ""
	    for lake_color in measurements:
	        measurements_report += \'\'\'
	            {0}:
	        \'\'\'.format(lake_color)
	
	        for lake_measurements in measurements[lake_color]:
	            measurements_report += \'\'\'
	                {0}: {1}
	            \'\'\'.format(lake_measurements, measurements[lake_color][lake_measurements])
	
	    report = \'\'\'
	        Lakes found finished in {0} seconds with {1}:
	        \'\'\'.format(elapsed_time,
	                   task_finish_cause(timeout, elapsed_time)) + \'\'\'
	            {0}
	        \'\'\'.format(measurements_report)
	
	    return report
	
	
	def bricks_mission_report(timeout, elapsed_time, measurements):
	    report = \'\'\'
	        Push bricks finished in {0} seconds with {1}:
	    \'\'\'.format(elapsed_time,
	               task_finish_cause(timeout, elapsed_time)) + \'\'\'
	            Bricks pushed off Mars: {0}
	        \'\'\'.format(measurements["bricks_pushed"])
	
	    return report
	
	
	def celebration_report(celebration_type):
	    report = \'\'\'
	        Celebrated with {0}
	    \'\'\'.format(celebration_type)
	
	    return report
	
	
	def generate_mission_report(timeouts, measurements):
	    f = open("resources/mission_report.txt", "w")
	
	    mission_report = \
	        report_header(timeouts["global_timeout"],
	                      timeouts["global_time_elapsed"]) + \
	        lakes_mission_report(timeouts["find_lakes_timeout"],
	                             timeouts["find_lakes_elapsed_time"],
	                             measurements['lakes']) + \
	        bricks_mission_report(timeouts["push_bricks_timeout"],
	                              timeouts["push_bricks_elapsed_time"],
	                              measurements['bricks']) + \
	        celebration_report(measurements['celebrate'])
	
	    f.write(mission_report)
	
	'''
	def static toAPI_parking()'''
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
	
	BLACK = get_black()
	WHITE = get_white()
	
	
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
	        color_collision_protocol([get_left_sensor().color != BLACK and get_left_sensor().color != WHITE,
	                                  get_middle_sensor().color != BLACK and get_middle_sensor().color != WHITE,
	                                  get_right_sensor().color != BLACK and get_right_sensor().color != WHITE])
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
	
	        if cs[0] == WHITE or cs[1] == WHITE or cs[2] == WHITE:
	            continue
	
	        if arb.read_message()[0] == "ultrasonic" \
	                or arb.read_message()[0] == "touch" \
	                or (cs[0] != BLACK or cs[1] != BLACK or cs[2] != BLACK):
	                    arb.set_message(("clear", None))
	                    direction = toggle_direction(direction)
	                    move_both_in_direction(15, direction, 1)
	
	
	def park_rover(border_color):
	    move_to_border(border_color)
	    position_on_border_line(border_color)
	    turn_90_degrees()
	    move_to_corner(border_color)
	
	'''
	def static toAPI_roverBluetooth()'''
	#!/usr/bin/env python3
	
	import bluetooth
	
	# SERVER_MAC = 'CC:78:AB:50:B2:46' # brick 11
	SERVER_MAC = '00:17:E9:B2:1E:41' # brick 9
	
	message = ("clear", None)
	
	
	def connect():
	    port = 3
	    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
	    server_sock.bind((SERVER_MAC, port))
	    server_sock.listen(1)
	    print('Listening...')
	    client_sock, address = server_sock.accept()
	    print('Accepted connection from ', address)
	    return client_sock, client_sock.makefile('r'), client_sock.makefile('w')
	
	
	def disconnect(sock):
	    sock.close()
	
	
	def write_to_socket(sock_out, message):
	    sock_out.write(str(message) + '\n')
	    sock_out.flush()
	
	
	def read_message():
	    return message
	
	
	def set_message(value):
	    global message
	    message = value
	
	
	def listen(sock_in, sock_out, mission_ongoing):
	    global message
	
	    while mission_ongoing:
	        # converting serialized string to tuple
	        # each tuple is formed of the sensor from which the
	        # information come and the value given by that sensor
	        message = eval(sock_in.readline())
	
	
	'''
	def static toAPI_touch()'''
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
	
	'''
	def static toAPI_ultrasonic()'''
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
	
	'''
	def static toAPI_wheelMovement()'''
	from ev3dev2.motor import LargeMotor, MoveTank, OUTPUT_A, OUTPUT_D, SpeedPercent
	
	left_wheel = LargeMotor(OUTPUT_A)
	right_wheel = LargeMotor(OUTPUT_D)
	both_wheels = MoveTank(OUTPUT_A, OUTPUT_D)
	
	
	def move_both_for_seconds(percent_left, seconds, blocking=True, percent_right=None):
	    both_wheels.on_for_seconds(SpeedPercent(percent_left),
	                               SpeedPercent(percent_right if percent_right else percent_left),
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
	
	
	def move_both_in_direction(percent, direction, seconds=None):
	    if seconds:
	        if direction == "forward":
	            move_both_for_seconds(percent, seconds)
	        else:
	            move_both_for_seconds(-percent, seconds)
	    else:
	        if direction == "forward":
	            move_both(percent)
	        else:
	            move_both(-percent)
	
	'''
}