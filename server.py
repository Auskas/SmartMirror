#!/usr/bin/env python3

import subprocess
import socket
import hashlib
import re

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
        self.command = ''
        print('Server is running...')
        #self.listener()

    def check_password(self):
        self.conn.sendall(b'Connected to server. Enter your credentials:')
        while True:
            try:
                data = self.conn.recv(1024)
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

    def listener(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((self.HOST, self.PORT))
                    s.listen()
                except Exception as error:
                    print('Socket is already in use!')
                self.conn, self.addr = s.accept()
                print('Connected by', self.addr)
                password = self.check_password()
                if password == False:
                    print('Wrong credentials')
                    self.conn.sendall(b'Connection refused')
                    s.close()
                else:
                    print('Access granted')
                    self.conn.sendall(b'Access granted')
                with self.conn:
                    while True:
                        try:
                            data = self.conn.recv(1024)
                            if not data:
                                break
                            #print(f'Sending back: {data.decode()}')
                            self.conn.sendall(data)
                            self.command = data.decode()
                            self.gesturesAssistant.command = 'RemoteControl'
                            self.voiceAssistant.cmd_handler(self.command)
                            #self.gesturesAssistant.command = 'None'
                            self.command = ''
                        except Exception as exc:
                            print('Connection lost!')
                            break

if __name__ == '__main__':
    class VoiceAssistant:
        def __init__(self):
            pass
        def cmd_handler(self, cmd):
            pass
    voiceAssistant = VoiceAssistant()
    server = Server(voiceAssistant)
    server.listener()


