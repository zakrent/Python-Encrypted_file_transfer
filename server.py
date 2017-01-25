#!/usr/bin/python3

import os, socket, logging, _thread, rsa
from cryptography.fernet import Fernet

def send(connSocket, message, noEncoding = False, Fernet = None):
	logging.debug(message)
	if Fernet and noEncoding:
		message = Fernet.encrypt(message)
	elif Fernet:
		message = Fernet.encrypt(message.encode('UTF-8'))
		noEncoding = True

	if noEncoding:
		connSocket.send(message)
	else:
		connSocket.send(message.encode('utf-8'))

def recive(connSocket, noDecode = False, Fernet = None):
	message = connSocket.recv(2048)
	logging.debug(message)
	if Fernet:
		message = Fernet.decrypt(message)
	if noDecode:
		return message

	return message.decode("UTF-8")

def isReady(connSocket, Fernet):
	data = recive(connSocket, False, Fernet)
	if data == "RDY":
		return True
	else:
		return False

def listfiles(connSocket, Fernet):
	send(connSocket, 'ALS', False, Fernet)
	filelist = os.listdir('files')
	for filename in filelist:
		timeout = 2000
		while not isReady(connSocket, Fernet) and timeout > 0:
			timeout -= 1
		send(connSocket, filename, False, Fernet)
	timeout = 2000
	while not isReady(connSocket, Fernet) and timeout > 0:
		timeout -= 1
	send(connSocket, 'END', False, Fernet)

def sendfile(connSocket, filename, Fernet):
	filedir = 'files/'+filename
	if not os.path.exists(filedir) or str(filename)=="":
		send(connSocket, "UNF", False, Fernet)
		return
	filesize = os.path.getsize(filedir)
	with open(filedir, 'rb') as f:
		send(connSocket, 'ASF', False, Fernet)
		timeout = 2000
		while not isReady(connSocket, Fernet) and timeout > 0:
			timeout -= 1
		send(connSocket, filename, False, Fernet)
		while not isReady(connSocket, Fernet) and timeout > 0:
			timeout -= 1
		send(connSocket, str(filesize), False, Fernet)
		data = f.read(2048)
		while data:
			if len(data) % 2048 != 0:
				data += f.read(len(data) % 2048)
			logging.info(len(Fernet.encrypt(data)))
			send(connSocket, data, True, Fernet)
			data = f.read(2048)

def authorize(connSocket, AESKey):
	send(connSocket, "AUT")
	data = recive(connSocket)
	password = "LOL123"
	if data == password:
		send(connSocket, "KEY")
		PubKeyString = recive(connSocket, True)
		logging.debug(PubKeyString)
		PubKey = rsa.PublicKey.load_pkcs1(PubKeyString)
		AESKey = rsa.encrypt(AESKey, PubKey)
		send(connSocket, AESKey, True)
		return PubKey
	else:
		send(connSocket, "ERR")
		return None

def handler(connSocket):
	connSocket.settimeout(60)
	try:
		peerName = connSocket.getpeername()[0]
		AESKey = Fernet.generate_key()
		if authorize(connSocket, AESKey):
			f = Fernet(AESKey)
			while True:
				command = recive(connSocket, False, f)
				logging.info(peerName+" "+command)
				if command[:3] == 'LST':
					listfiles(connSocket, f)
				elif command[:3] == 'GET':
					sendfile(connSocket, command[4:], f)
				else:
					send(connSocket, "UNK", False, f)
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
		port = 5000

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
