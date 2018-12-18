#!/usr/bin/env python3

import bluetooth

SERVER_MAC = 'CC:78:AB:50:B2:46'

angle = 0

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

def write_to_socket(sock_out, signal):
    sock_out.write(str(signal) + '\n')
    sock_out.flush()

def listen(sock_in, sock_out, mission_ongoing):
    global angle
    
    while mission_ongoing:
        angle = int(sock_in.readline())
        # print("AngleBluetoothListener: ", angle)

