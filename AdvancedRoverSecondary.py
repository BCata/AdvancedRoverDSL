#!/usr/bin/env python3

import bluetooth
import threading
from ev3dev2.sensor.lego import GyroSensor
from ev3dev2._platform.ev3 import INPUT_1, INPUT_2, INPUT_3, INPUT_4


SERVER_MAC = 'CC:78:AB:50:B2:46'
mission_ongoing = True
gs = GyroSensor(INPUT_3)
gs.mode = 'GYRO-ANG'

def connect():
    port = 3
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    print('Connecting...')
    sock.connect((SERVER_MAC, port)) 
    print('Connected to ', SERVER_MAC)
    return sock, sock.makefile('r'), sock.makefile('w')

def disconnect(sock):
    sock.close() 

def write_to_socket(sock_out, angle):
    sock_out.write(str(angle) + '\n')
    sock_out.flush()

def run():
    reset_gyro()
    sock, sock_in, sock_out = connect()
    sender = threading.Thread(target=gyro, args=(sock_in, sock_out))
    sender.start()

    listener = threading.Thread(target=listen, args=(sock_in, sock_out))
    listener.start()

    while mission_ongoing: 
        pass

    disconnect(sock_in)
    disconnect(sock_out)
    disconnect(sock)    
    print("Slave disconnected")

def listen(sock_in, sock_out):
    signal = str(sock_in.readLine())
    if(signal == "reset_gyro"):
        reset_gyro()

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