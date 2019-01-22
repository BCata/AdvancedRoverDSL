package mars.rover.generator

import mars.rover.dSL.Mission
import mars.rover.dSL.FindLakes
import mars.rover.dSL.PushBricks
import mars.rover.dSL.ParkRover
import mars.rover.dSL.Celebrate
import mars.rover.dSL.Task
import mars.rover.dSL.Color

class CodeGenerator {
	def static toMainCode(Mission root) '''
	#!/usr/bin/env python3
	import sys
	import threading
	from math import floor
	
	from time import time
	from ev3dev2.sound import Sound
	
	import api.rover_bluetooth as arb
	from api.celebration import celebrate
	from api.mission_report import generate_mission_report
	
	from api.touch import detect_touch, get_touch_encountered, set_touch_encountered
	from api.parking import park_rover
	from api.measurements import measure_lake, get_measurements
	from api.wheel_movement import move_both, stop_both, move_both_for_seconds
	from api.color import color_collision_protocol, detect_color, detect_line
	from api.color import get_right_sensor, get_left_sensor, get_middle_sensor
	from api.color import get_red, get_blue, get_green, get_yellow, get_white, get_black
	from api.ultrasonic import ultrasonic_collision_protocol, ultrasonic_back_collision_protocol
	
	BORDER_COLOR = get_«root.borderColor»()
	«root.groundColor.toString().toUpperCase()» = get_«root.groundColor»()
	«FOR task: root.tasks»	
		«generateColors(task.name)»
	«ENDFOR»
	
	GLOBAL_TIMEOUT = «root.duration.dl»
	
	«FOR task: root.tasks»
		«generateTimeout(task.name)»
	«ENDFOR»
	
	s = Sound()
	cs_left = get_left_sensor()
	cs_middle = get_middle_sensor()
	cs_right = get_right_sensor()
	
	«FOR task: root.tasks»
		«generateFunctions(task.name)»
	«ENDFOR»
	
	«generateMissionOngoing(root)»
	
	«IF root.createReport !== null»
		«generateReportCode(root)»
	«ENDIF»
	
	 «generateMain(root)»
	 
	'''
	
	def static generateMain(Mission root)'''
	if __name__ == "__main__":
		sock, sock_in, sock_out = arb.connect()
		listener = threading.Thread(target=arb.listen, args=(sock_in, sock_out, mission_ongoing))
		listener.start()
		
		lakes_to_find = «FOR task: root.tasks BEFORE "(" AFTER ")"»«IF task.name instanceof FindLakes»«val findLakes = task.name as FindLakes»«FOR lake: findLakes.lakes SEPARATOR ", "»«lake.color.toString().toUpperCase()»«ENDFOR»«ENDIF»«ENDFOR»
		
		mission_duration = sys.maxsize
		find_lakes_duration = sys.maxsize
		push_bricks_duration = sys.maxsize
		
		# start timers
		globalStart = time()
		
		while mission_ongoing():
			color_collision_protocol(detect_line(BORDER_COLOR))
			ultrasonic_back_collision_protocol()
			detect_lakes(detect_color(), lakes_to_find)
			move_both(SPEED)
            «var pushBricksExists = false»«FOR task: root.tasks»«IF task.name instanceof PushBricks»«{pushBricksExists=true;""}»«ENDIF»«ENDFOR»
            «IF pushBricksExists»push_bricks()«ELSE»
            message = arb.read_message()
            if message[0] == "ultrasonic":
                ultrasonic_collision_protocol()
                arb.set_message(("clear", None))
            «ENDIF»
			
			detect_touch()
			
		# mission completed (or timeout exceeded)
		stop_both()
		s.speak("Exploration finished")
		
        «FOR task: root.tasks»«IF task.name instanceof Celebrate»«val celebrate = task.name as Celebrate»
        s.speak("Let us celebrate")
        celebrate("«celebrate.celebrate»")
        «ENDIF»«ENDFOR»

        «FOR task: root.tasks»«IF task.name instanceof ParkRover»
        s.speak("Now let me park")
		park_rover(BORDER_COLOR)
		stop_both()
        «ENDIF»«ENDFOR»
		
        «IF root.createReport !== null»
		create_mission_report()
		s.speak("Mission report generated")
        «ENDIF»

		s.speak("Mission")
		arb.write_to_socket(sock_out, False)
	'''
		
	def static dispatch generateMissionOngoingConditions(FindLakes find) ''' and lakes_found'''
	def static dispatch generateMissionOngoingConditions(PushBricks push) ''' and bricks_pushed'''	
	def static dispatch generateMissionOngoingConditions(ParkRover park) ''''''
	def static dispatch generateMissionOngoingConditions(Celebrate celebrate) ''''''
	
	def static generateMissionOngoing(Mission root)'''
	def mission_ongoing():
	    global mission_duration
	
	    # global timeout exceeded
	    if time() - globalStart >= GLOBAL_TIMEOUT:
	        mission_duration = floor(time() - globalStart)
	        return False
	
	    # if all missions completed
	    if True«FOR t: root.tasks»«generateMissionOngoingConditions(t.name)»«ENDFOR»:  		
	        mission_duration = floor(time() - globalStart)
	        return False
	
	    return True
	'''
	
	def static generateReportCode(Mission root) '''
	def create_mission_report():
	        timeouts = {'global_timeout': GLOBAL_TIMEOUT,
	                    'global_time_elapsed': mission_duration,
	                    «FOR task: root.tasks SEPARATOR ","»
	                        «generateReportTimeouts(task.name)»
	                    «ENDFOR»
	                    }
	   
	        measurements = {
	                        «FOR task: root.tasks SEPARATOR ","»
	                            «generateReportMeasurements(task.name)»
	                        «ENDFOR»
	                        }
	   
	        generate_mission_report(timeouts, measurements)
	    
	'''
	
	def static dispatch generateReportMeasurements(FindLakes mission) '''
                        'lakes': get_measurements()
    '''
    def static dispatch generateReportMeasurements(PushBricks mission) '''
                        'bricks_pushed': "{0} out of {1}".format(initial_number_of_bricks - bricks_to_push,
                                                                 initial_number_of_bricks)
    '''
    def static dispatch generateReportMeasurements(ParkRover mission) ''''''
    def static dispatch generateReportMeasurements(Celebrate mission) '''
                        'celebrate': '«mission.celebrate»'
    '''
   
    def static dispatch generateReportTimeouts(FindLakes task) '''
                'find_lakes_timeout': FIND_LAKES_TIMEOUT,
                'find_lakes_elapsed_time': min(find_lakes_duration, mission_duration)
    '''
    def static dispatch generateReportTimeouts(PushBricks task) '''
                'push_bricks_timeout': PUSH_BRICKS_TIMEOUT,
                'push_bricks_elapsed_time': min(push_bricks_duration, mission_duration)
    '''
    def static dispatch generateReportTimeouts(ParkRover task) ''''''
    def static dispatch generateReportTimeouts(Celebrate task) ''''''
	
	def static dispatch generateFunctions(FindLakes find) '''
	def process_lake(color_val, color_name):
	    s.speak(color_name + "found")
	    measure_lake(color_val)
	    color_found[color_val] = True
	
	    # set mission as completed if all lakes are found
	    global lakes_found, find_lakes_duration
	    lakes_found = all(list(color_found.values()))
	
	    if lakes_found:
	        find_lakes_duration = floor(time() - globalStart)
	        
	def detect_lakes(color_sensor_tuple, lakes):
	    color_sensor_firing = [False, False, False]
	    has_time_elapsed = time() - globalStart >= FIND_LAKES_TIMEOUT
	
	    global lakes_found, find_lakes_duration
	    if has_time_elapsed:
	        lakes_found = True
	        find_lakes_duration = floor(time() - globalStart)
	
	    for index, color in enumerate(color_sensor_tuple):
	        if color in lakes:
	            color_sensor_firing[index] = True
	            stop_both()
	            if color == RED and not color_found[RED] and not has_time_elapsed:
	                process_lake(RED, "Red")
	            if color == YELLOW and not color_found[YELLOW] and not has_time_elapsed:
	                process_lake(YELLOW, "Yellow")
	            if color == BLUE and not color_found[BLUE] and not has_time_elapsed:
	                process_lake(BLUE, "Blue")
	            if color == GREEN and not color_found[GREEN] and not has_time_elapsed:
	                process_lake(GREEN, "Green")
	
	    color_collision_protocol(color_sensor_firing)
	    ultrasonic_back_collision_protocol()
	
	'''
	def static dispatch generateFunctions(PushBricks push) '''
	def push_bricks():
	    global bricks_to_push, bricks_pushed, previous_ultrasonic_distance, current_ultrasonic_distance, push_bricks_duration
	
	    has_time_elapsed = time() - globalStart >= PUSH_BRICKS_TIMEOUT
	
	    # detect ultrasonic input from secondary brick
	    message = arb.read_message()
	
	    if message[0] == "ultrasonic":
	        if bricks_to_push == 0 or has_time_elapsed:
	            # done pushing bricks
	            bricks_pushed = True
	            push_bricks_duration = floor(time() - globalStart)
	            ultrasonic_collision_protocol()
	        else:
	            # prepare decrement number of bricks after brick falls
	            previous_ultrasonic_distance = current_ultrasonic_distance
	            current_ultrasonic_distance = message[1]
	
	        arb.set_message(("clear", None))
	    else:
	        current_ultrasonic_distance = 0
	
	    # if brick has fallen off the edge, decrement counter
	    if get_touch_encountered():
	        set_touch_encountered(False)
	    else:
	        if bricks_to_push > 0 and previous_ultrasonic_distance != 0 and current_ultrasonic_distance == 0:
	            bricks_to_push -= 1
	            previous_ultrasonic_distance = current_ultrasonic_distance = 0
	
	'''
	def static dispatch generateFunctions(ParkRover park) ''''''
	def static dispatch generateFunctions(Celebrate celebrate) ''''''
	
	def static dispatch generateColors(FindLakes find)'''
		«FOR lake: find.lakes»
			«lake.color.toString().toUpperCase()» = get_«lake.color»()
		«ENDFOR»
		
		color_found = {
		«FOR lake: find.lakes SEPARATOR ","»	«lake.color.toString().toUpperCase()» = False
		«ENDFOR»
		}
	'''
	def static dispatch generateColors(PushBricks push)''''''
	def static dispatch generateColors(ParkRover park)''''''
	def static dispatch generateColors(Celebrate celebrate)''''''
	
	def static dispatch generateTimeout(FindLakes find)'''
	FIND_LAKES_TIMEOUT = «IF find.untilTermination !== null»sys.maxsize«ELSE»«find.duration.dl»«ENDIF»
	lakes_found = False
	
	'''
	def static dispatch generateTimeout(PushBricks push)'''
	PUSH_BRICKS_TIMEOUT = «IF push.untilTermination !== null»sys.maxsize«ELSE»«push.duration.dl»«ENDIF»
	initial_number_of_bircks = «push.number»
	bricks_pushed = False
	bricks_to_push = initial_number_of_bricks
	current_ultrasonic_distance = 0
	previous_ultrasonic_distance = 0
	
	'''
	def static dispatch generateTimeout(ParkRover park)''''''
	def static dispatch generateTimeout(Celebrate celebrate)''''''
	
	def static toSecondaryCode(Mission root) '''
	#!/usr/bin/env python3
	
	import sys
	import bluetooth
	import threading
	
	from time import sleep
	from ev3dev2.sound import Sound
	from ev3dev2.sensor.lego import TouchSensor, UltrasonicSensor
	from ev3dev2._platform.ev3 import INPUT_1, INPUT_2, INPUT_3, INPUT_4
	
	
	SERVER_MAC = «IF root.masterMAC !== null»'«root.masterMAC»'«ELSE»'00:17:E9:B2:1E:41'«ENDIF»
	
	mission_ongoing = True
	
	s = Sound()
	gs = GyroSensor(INPUT_3)
	gs.mode = 'GYRO-ANG'
	ts_left = TouchSensor(INPUT_1)
	ts_right = TouchSensor(INPUT_4)
	us_front = UltrasonicSensor(INPUT_2)
	us_front.mode = 'US-DIST-CM'
	
	
	def connect():
	    port = 3
	    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
	    print('Connecting...')
	    sock.connect((SERVER_MAC, port)) 
	    print('Connected to ', SERVER_MAC)
	    return sock, sock.makefile('r'), sock.makefile('w')
	
	
	def disconnect(sock):
	    sock.close() 
	
	
	def write_to_socket(sock_out, message):
	    sock_out.write(str(message) + '\n')
	    sock_out.flush()
	
	
	def run():
	    
	    for i in range(1,10):
	        try:
	            print("Attempt {attempt} out of 10".format(attempt=i))
	            sock, sock_in, sock_out = connect()
	        except bluetooth.btcommon.BluetoothError:
	            continue
	        except:
	            print(sys.exc_info()[0])
	        finally:
	            sleep(3)
	        break
	
	    listener = threading.Thread(target=listen, args=(sock_in, sock_out))
	    listener.start()
	
	    while mission_ongoing:
	        touch = touch_detection()
	        if touch[0] or touch[1]:
	            write_to_socket(sock_out, ("touch",touch))
	
	        distance = ultrasonic_detection()
	        if distance:
	            write_to_socket(sock_out, ("ultrasonic", distance))
	
	
	    disconnect(sock_in)
	    disconnect(sock_out)
	    disconnect(sock)    
	    s.speak("completed")
	    print("Slave disconnected")
	
	
	def ultrasonic_detection():
	    if us_front.value()/10 < 15:
	        return us_front.value()
	
	
	def touch_detection():
	    return (ts_left.is_pressed,ts_right.is_pressed)
	
	
	def listen(sock_in, sock_out):
	    global mission_ongoing
	    mission_ongoing = eval(sock_in.readline())
	
	run()
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