#!/usr/bin/python3

import socket
import sys
import logging

def handler(s):
	data = s.recv(2048).decode('UTF-8')
	if data == "ASF":
		s.send("RDY".encode('UTF-8'))
		data = s.recv(2048).decode('UTF-8')
		with open(data, 'wb') as f:
			s.send("RDY".encode('UTF-8'))
			filesize = int(s.recv(2048).decode('UTF-8'))
			recived = 0
			while filesize - recived > 0:
				data = s.recv(2048)
				recived += len(data)
				f.write(data)
	elif data == "ALS":
		while data != "END":
			s.send("RDY".encode('UTF-8'))
			data = s.recv(2048).decode('UTF-8')
			if data != "END":
				print(data)
	elif data == "UNK":
		logging.warning("Unknown command")
	elif data == "UNF":
		logging.warning("Unknown file")
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

		s = socket.socket()
		s.connect(('127.0.0.1',5001))
		logging.info("Connected")
		data = s.recv(2048).decode('UTF-8')
		if data == "AUT":
			passw = input("Password ->")
			s.send(passw.encode('UTF-8'))
			data = s.recv(2048).decode('UTF-8')
			if data == "ACK":
				while True:
					command = input("->")
					s.send(command.encode('UTF-8'))
					handler(s)
	except:
		logging.error(sys.exc_info()[0])
		s.close()

if __name__=='__main__':
	main()
