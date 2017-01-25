#!/usr/bin/python3

import socket, sys, logging, rsa, time
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

def recive(connSocket, noDecode = False, Fernet = None, numberOfBytes = 2048):
	message = connSocket.recv(numberOfBytes)
	logging.debug(message)
	if Fernet:
		message = Fernet.decrypt(message)
	if noDecode:
		return message

	return message.decode("UTF-8")

def handler(s, Fernet):
	data = recive(s, False, Fernet)
	if data == "ASF":
		send(s,"RDY", False, Fernet)
		data = recive(s, False, Fernet)
		startTime = time.time()
		with open(data, 'wb') as f:
			send(s,"RDY", False, Fernet)
			filesize = int(recive(s, False, Fernet))
			recived = 0
			percent = 0
			lastPercent = 0
			lastRecived = 0
			LastTime = 0
			print("%i/%i %i%%"%(recived, filesize, percent))
			while filesize - recived > 0:
				data = recive(s, True)
				if len(data) % 2828 != 0 and filesize-recived > 2828 - len(data):
					data += recive(s, True, None, 2828 - len(data))
				data = Fernet.decrypt(data)
				recived += len(data)
				percent = int(recived/filesize*100)
				if percent - lastPercent  > 5:
					speed = (((recived-lastRecived)/(time.time()-LastTime))/1000000)*8
					if speed > 1 :
						left = ((filesize - recived)/1000000)/(speed/8)
					else:
						left = 0
					print("%i/%i %i%% %i MBits/s %i seconds left"%(recived, filesize, percent, speed, left))
					lastPercent = percent
					LastTime = time.time()
					lastRecived = recived
				f.write(data)
		logging.info("%i bytes downloaded."%(recived))
		logging.info("Download time: %f s"%(time.time()-startTime))
	elif data == "ALS":
		while data != "END" and data:
			send(s, "RDY", False, Fernet)
			data = recive(s, False, Fernet)
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
		return None

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
			if AESKey != b"":
				f = Fernet(AESKey)
				while True:
					command = input("->")
					if command:
						if command == "EXIT":
							exit()
						else:
							send(s, command, False, f)
							handler(s, f)
	except:
		logging.error(sys.exc_info()[0])
		s.close()

if __name__=='__main__':
	main()
