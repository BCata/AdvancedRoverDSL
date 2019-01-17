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
        # each tupple is formed of the sensor from which the
        # information come and the value given by that sensor
        message = eval(sock_in.readline())
        # print("Bluetooth received: ", message)

