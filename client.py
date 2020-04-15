#!/usr/bin/env python3

import socket
import subprocess
import re

def ip_address_discovery():
    process = subprocess.Popen(PING_COMMAND, stdout=subprocess.PIPE, shell=True)
    stdout = process.communicate()[0].strip()
    ip_address_regex = re.compile(r'\d+.\d+.\d+.\d+')
    ip_address = ip_address_regex.search(stdout.decode('utf-8'))
    if ip_address == None:
        return None
    return ip_address.group()

PING_COMMAND = 'ping gesell.local -c 3'
#PING_COMMAND = 'ping auskas-ubuntu.local -c 3'
HOST = ip_address_discovery()
if HOST == None:
    print('Cannot find the server IP address. Terminating the program...')
    input('Press ENTER to quit the client')
else:
    print(f'Server has been discovered: IP address {HOST}')
    PORT = 1175        # The port used by the server

    message_string = None

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        data = s.recv(1024)
        print(data.decode())
        while message_string != 'quit':
            message_string = input()
            message_bytes = message_string.encode('utf-8')
            s.sendall(message_bytes)
            data = s.recv(1024)
            print(f'Server response: {data.decode()}')
            if data.decode() == 'Connection refused':
            	print('Server has terminated the connection')
            	input('Press ENTER to terminate the client')
            	break
