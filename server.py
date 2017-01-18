#!/usr/bin/python3

import os
import socket
import logging
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
	timeout = 2000
	while not isReady(connSocket) and timeout > 0:
		timeout -= 1
	send(connSocket, 'END')

def sendfile(connSocket, filename):
	filedir = 'files/'+filename
	if not os.path.exists(filedir) or str(filename)=="":
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
	connSocket.settimeout(60)
	try:
		peerName = connSocket.getpeername()[0]
		if authorize(connSocket):
			while True:
				command = recive(connSocket)
				logging.info(peerName+" "+command)
				if command[:3] == 'LST':
					listfiles(connSocket)
				elif command[:3] == 'GET':
					sendfile(connSocket, command[4:])
				else:
					send(connSocket, "UNK")
		connSocket.close()
	except:
		logging.error(sys.exc_info()[0])
	finally:
		logging.info(peerName + " closed connection")
		connSocket.close()
		return

def main():
	try:
		logging.basicConfig(
			filename='server.log',
			level=logging.INFO,
			format= '[%(asctime)s] %(levelname)s - %(message)s',
			datefmt='%H:%M:%S'
	 	)
		terminal = logging.StreamHandler()
		terminal.setLevel(logging.INFO)
		formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
		terminal.setFormatter(formatter)
		logging.getLogger("").addHandler(terminal)

		host = '127.0.0.1'
		port = 5001

		listenSocket = socket.socket()
		listenSocket.bind((host,port))

		while True:
			listenSocket.listen(5)
			connSocket, connAddres = listenSocket.accept()
			logging.info("Connection "+connSocket.getpeername()[0])
			_thread.start_new_thread(handler, (connSocket,))
	except:
		logging.error(sys.exc_info()[0])
	finally:
		logging.warning("Program closed")
		listenSocket.close()
		return

if __name__=='__main__':
	main()
