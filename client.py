#!/usr/bin/python3

import socket
import sys
import logging
import rsa

def send(connSocket, message, noEncoding = False):
	logging.debug(message)
	if noEncoding:
		connSocket.send(message)
	else:
		connSocket.send(message.encode('utf-8'))

def recive(connSocket, noDecode = False, noEncryption = 0):
	if noDecode:
		return connSocket.recv(2048)
	return connSocket.recv(2048).decode('utf-8')

def handler(s):
	data = recive(s)
	if data == "ASF":
		send(s,"RDY")
		data = recive(s)
		with open(data, 'wb') as f:
			send(s,"RDY")
			filesize = int(recive(s))
			recived = 0
			while filesize - recived > 0:
				data = recive(s, True)
				recived += len(data)
				f.write(data)
	elif data == "ALS":
		while data != "END" and data:
			send(s, "RDY")
			data = recive(s)
			if data != "END":
				print(data)
	elif data == "UNK":
		logging.warning("Unknown command")
	elif data == "UNF":
		logging.warning("Unknown file")

def authorize(s, pubKey, privKey):
	password = input("Password -> ")
	send(s, password)
	data = recive(s)
	if data == "KEY":
		logging.info("Sending encryption key...")
		send(s, pubKey.save_pkcs1(), True)
		logging.info("Reciving encryption key...")
		AESKey = recive(s, True)
		while not AESKey:
			ESKey = recive(s, True)
		AESKey = rsa.decrypt(AESKey, privKey)
		logging.debug(AESKey)
		return AESKey
	else:
		return 0

def main():
	try:
		logging.basicConfig(
			filename='client.log',
			level=logging.INFO,
			format= '[%(asctime)s] %(levelname)s - %(message)s',
			datefmt='%H:%M:%S'
	 	)
		terminal = logging.StreamHandler()
		terminal.setLevel(logging.INFO)
		formatter = logging.Formatter('%(levelname)s : %(message)s')
		terminal.setFormatter(formatter)
		logging.getLogger("").addHandler(terminal)

		(pubKey, privKey) = rsa.newkeys(1024)

		s = socket.socket()
		s.connect(('127.0.0.1',5000))
		logging.info("Connected")
		data = recive(s)
		if data == "AUT":
			AESKey = authorize(s, pubKey, privKey)
			if AESKey !=0:
				while True:
					command = input("->")
					logging.debug(command)
					send(s, command)
					handler(s)
	except:
		logging.error(sys.exc_info()[0])
		s.close()

if __name__=='__main__':
	main()
