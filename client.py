#!/usr/bin/env python3

import socket
import subprocess
import re
import os
import json
from Crypto.PublicKey import RSA

def ip_address_discovery():
    process = subprocess.Popen(PING_COMMAND, stdout=subprocess.PIPE, shell=True)
    stdout = process.communicate()[0].strip()
    ip_address_regex = re.compile(r'\d+.\d+.\d+.\d+')
    ip_address = ip_address_regex.search(stdout.decode('utf-8'))
    if ip_address == None:
        return None
    return ip_address.group()

def encrypted_message(message):
    return public_key.encrypt(message.encode('utf-8'), 32)[0]

with open(f'encryption{os.sep}public_RSA.key', 'r') as file:
    public_key = RSA.importKey(file.read())
with open(f'encryption{os.sep}private_RSA.key', 'r') as file:
    private_key = RSA.importKey(file.read())

capabilities = None

#PING_COMMAND = 'ping gesell.local -c 3'
PING_COMMAND = 'ping auskas-ubuntu.local -c 3'
HOST = ip_address_discovery()
#HOST = '172.20.10.2'
if HOST == None:
    print('Cannot find the server IP address. Terminating the program...')
    input('Press ENTER to quit the client')
else:
    print(f'Server has been discovered: IP address {HOST}')
    PORT = 1175        # The port used by the server

    message_string = None

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        data = private_key.decrypt(s.recv(1024))
        print(data.decode())
        while message_string != 'quit':
            message_string = input()
            s.sendall(encrypted_message(message_string))
            data = s.recv(1024)
            data = private_key.decrypt(data)
            data = data.decode()
            print(f'Server response: {data}')
            if data == 'Connection refused':
            	print('Server has terminated the connection')
            	input('Press ENTER to terminate the client')
            	break
            elif data.find('Capabilities') != -1:
                data = data[data.find('{'):]
                capabilities = json.loads(data)


