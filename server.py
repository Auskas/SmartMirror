#!/usr/bin/env python3

import subprocess
import socket
import hashlib
import re
import os
import json
import copy
from Crypto.PublicKey import RSA

class Server:

    def __init__(self, voiceAssistant, gesturesAssistant):
        self.voiceAssistant = voiceAssistant
        self.gesturesAssistant = gesturesAssistant

        process = subprocess.Popen('hostname --all-ip-addresses', stdout=subprocess.PIPE, shell=True)
        stdout = process.communicate()[0].strip()
        ip_address_regex = re.compile(r'\d+.\d+.\d+.\d+')
        ip_address = ip_address_regex.search(stdout.decode('utf-8'))
        if ip_address == None:
            print('Cannot get the IP address. Using the loopback interface.')
            self.HOST = '127.0.0.1'
        else:
            print(f'The IP address to listen: {ip_address.group()}')
            self.HOST = ip_address.group()  # IP address to listen is the main network interface address.
        self.PORT = 1175        # Port to listen on (non-privileged ports are > 1023)
        with open('hashpass.dat', 'r') as file:
            self.hash = file.readlines()[0]

        with open(f'encryption{os.sep}private_RSA.key', 'r') as file:
            key = file.read()
            self.private_key = RSA.importKey(key)
            #print(self.private_key)
        with open(f'encryption{os.sep}public_RSA.key', 'r') as file:
            key = file.read()
            #print(key, type(key))
            self.public_key = RSA.importKey(key)
            #print(self.public_key)
        self.command = ''
        print('Server is running...')
        #self.listener()

    def check_password(self):
        #encrypted_message = self.public_key.encrypt(b'Connected to server. Enter your credentials:', 32)
        #print(encrypted_message)
        self.conn.sendall(self.encrypted_message('Connected to server. Enter your credentials:'))
        while True:
            try:
                data = self.conn.recv(1024)
                data = self.private_key.decrypt(data)
                if hashlib.sha256(data).hexdigest() == self.hash:
                    return True
                else:
                    return False
                if not data:
                    break
            except Exception as exc:
                print('Connection lost!')
                break
        return False

    def encrypted_message(self, message):
        return self.public_key.encrypt(message.encode('utf-8'), 32)[0]

    def capabilities(self):
        cap = self.voiceAssistant.cmd.copy()
        for elem in cap:
            if isinstance(cap[elem], set):
                cap[elem] = list(cap[elem])
        return f'Capabilities {json.dumps(cap)}'


    def listener(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((self.HOST, self.PORT))
                    s.listen(3)
                except Exception as error:
                    print('Socket is already in use!')
                self.conn, self.addr = s.accept()
                print('Connected by', self.addr)
                password = self.check_password()
                if password == False:
                    print('Wrong credentials')
                    self.conn.sendall(self.encrypted_message('Connection refused'))
                    s.close()
                else:
                    print('Access granted')
                    cap = self.capabilities()
                    self.conn.sendall(self.encrypted_message(f'Access granted\n{cap}'))

                with self.conn:
                    while True:
                        try:
                            data = self.conn.recv(1024)
                            data = self.private_key.decrypt(data)
                            if not data:
                                break
                            #print(f'Sending back: {data.decode()}')
                            data = data.decode()
                            self.conn.sendall(self.encrypted_message(data))
                            self.command = data
                            self.gesturesAssistant.command = 'RemoteControl'
                            self.voiceAssistant.cmd_handler(self.command)
                            #self.gesturesAssistant.command = 'None'
                            self.command = ''
                        except Exception as exc:
                            print('Connection lost!')
                            print(exc)
                            break

if __name__ == '__main__':
    class VoiceAssistant:
        def __init__(self):
            self.cmd = {
                'youtube' : set(), 'weather': True, 'stocks': True,
                'marquee': True, 'spartak': True, 'clock': True, 'covid': True,
                'gesturesMode': False
                       }
            pass
        def cmd_handler(self, cmd):
            pass

    class GesturesAssistant:
        def _init__(self):
            self.command = None

    voiceAssistant = VoiceAssistant()
    gesturesAssistant = GesturesAssistant()
    server = Server(voiceAssistant, gesturesAssistant)
    server.listener()


