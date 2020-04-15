#! /usr/bin/python3
# hash_password.py

import hashlib

with open('hashpass.dat', 'w') as file:
	print('Enter the password:')
	password_string = input()
	password_hash = hashlib.sha256(password_string.encode('utf-8'))
	file.write(password_hash.hexdigest())
