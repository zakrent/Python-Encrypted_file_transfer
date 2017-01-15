#!/usr/bin/python3

import os
import socket
import _thread

def send(connSocket, message, noEncoding = False):
	if noEncoding:
		connSocket.send(message)
	else:
		connSocket.send(message.encode('utf-8'))

def recive(connSocket):
	return connSocket.recv(2048).decode('utf-8')

def isReady(connSocket):
	data = recive(connSocket)
	if data == "RDY":
		return True
	else:
		return False

def listfiles(connSocket):
	send(connSocket, 'ALS')
	filelist = os.listdir('files')
	for filename in filelist:
		timeout = 2000
		while not isReady(connSocket) and timeout > 0:
			timeout -= 1
		send(connSocket, filename)
	send(connSocket, 'END')

def sendfile(connSocket, filename):
	filedir = 'files/'+filename
	if not os.path.exists(filedir):
		send(connSocket, "UNF")
		return
	filesize = os.path.getsize(filedir)
	with open(filedir, 'rb') as f:
		send(connSocket, 'ASF')
		timeout = 2000
		while not isReady(connSocket) and timeout > 0:
			timeout -= 1
		send(connSocket, filename)
		while not isReady(connSocket) and timeout > 0:
			timeout -= 1
		send(connSocket, str(filesize))
		data = f.read(512)
		while data:
			send(connSocket, data, True)
			data = f.read(2048)

def authorize(connSocket):  #Placeholder
	send(connSocket, "AUT")
	data = recive(connSocket)
	password = "LOL123"
	if data == password:
		send(connSocket, "ACK")
		return True
	else:
		send(connSocket, "ERR")
		return False

def handler(connSocket):
	if authorize(connSocket):
		while True:
			command = recive(connSocket)
			print(command)
			if command[:3] == 'LST':
				listfiles(connSocket)
			elif command[:3] == 'GET':
				sendfile(connSocket, command[4:])
			else:
				send(connSocket, "UNK")
	connSocket.close()

def main():
	host = '127.0.0.1'
	port = 5000

	listenSocket = socket.socket()
	listenSocket.bind((host,port))

	while True:
		listenSocket.listen(5)
		connSocket, connAddres = listenSocket.accept()
		print("Connection"+str(connAddres))
		_thread.start_new_thread(handler, (connSocket,))
if __name__=='__main__':
	main()
