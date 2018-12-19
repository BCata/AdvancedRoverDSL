#!/usr/bin/env python3

import bluetooth
import threading
from time import sleep
from ev3dev2.sound import Sound
from ev3dev2.sensor.lego import GyroSensor, TouchSensor, UltrasonicSensor
from ev3dev2._platform.ev3 import INPUT_1, INPUT_2, INPUT_3, INPUT_4


# SERVER_MAC = 'CC:78:AB:50:B2:46'
SERVER_MAC = '00:17:E9:B2:1E:41'

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
    sock, sock_in, sock_out = connect()

    listener = threading.Thread(target=listen, args=(sock_in, sock_out))
    listener.start()

    while mission_ongoing: 
        distance = ultrasonic_detection()
        if distance:
            write_to_socket(sock_out, ("ultrasonic",distance))
        
        touch = touch_detection()
        if touch[0] or touch[1]:
            write_to_socket(sock_out, ("touch",touch))

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
    
def reset_gyro():
    gs.mode = 'GYRO-RATE'
    gs.mode = 'GYRO-ANG'
    print("Gyro reseted!")

def gyro(sock_in, sock_out):
    while mission_ongoing:
        print(gs.angle)
        write_to_socket(sock_out, gs.angle)
    print("gyro - Got out of while")

run()