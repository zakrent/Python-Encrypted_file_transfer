#!/usr/bin/python3

import socket

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
		print("Unknown command")
	elif data == "UNF":
		print("Unknown file")
def main():
	try:
		s = socket.socket()
		s.connect(('127.0.0.1',5000))
		print("Connected")
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
		s.close()
	except:
		s.close()
		return

if __name__=='__main__':
	main()
