#-*- encoding: utf-8 -*-
import socket
import sys
import cPickle as pickle
import threading
import errno
from sys import stdin
from time import sleep


def threaded(fn):
    def wrapper(*args, **kwargs):
		thread = NetworkSubroutine(target=fn, args=args, kwargs=kwargs)
		thread.start()
		return thread
    return wrapper

	
class TestData:
	def __init__(self, a, b):
		self.a = a
		self.b = b
	def cal(self):
		print self.a + self.b

class Address:
	def __init__(self, ip=None, port=None):
		self.ip = ip
		self.port = port
	def input(self, msg):
		print msg
		return stdin.readline()[:-1]
	def getInput(self):
		self.ip = self.input("please input ip address:")
		self.port = int(self.input("please input port number:"))

class P2Pconnection: #sync version
	def __init__(self):
		self.conn = None
		self.ip	  = socket.gethostbyname(socket.gethostname())
		self.port = 0
		
	def connect(self, address):
		try:
			client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client.connect((address.ip, address.port))
			self.conn = client
			return True, None
		except Exception as e:
			try:
				msg = str(e).decode('big5').strip()
			except:
				msg = str(e)
			return False, msg
		
	@threaded	
	def accept(self, info_callback=None, connected_callback=None, queue=None, stopHandle=None):
		local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		local.bind((self.ip, self.port))
		local.listen(1)
		info_callback(local.getsockname(), local, queue)
		self.listenSocket = local
		local.settimeout(0.5)
		while True:
			try:
				client, addr = local.accept()
				self.conn = client
				local.close()
				connected_callback(queue.get())
			except socket.timeout:
				pass
			except Exception as e:
				return
		
	def send(self, data):
		datastring = pickle.dumps(data)
		self.conn.send(datastring)
		
	@threaded	
	def recv(self, queue=None, stopHandle=None):
		while True:
			try:
				datastring = self.conn.recv(4096*10)
				dataObj    = pickle.loads(datastring)
				if(queue!=None):
					queue.put(dataObj)
				return
			except socket.error, e:
				err = e.args[0]
				if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
					sleep(1)
					continue
				else:
					print e
					queue.put(False)
					return
	
	def stopHandle(self):
		print 'stopEventHandle'
		self.listenSocket.close()
		

class NetworkSubroutine(threading.Thread):
	def __init__(self, target, args, kwargs):
		super(NetworkSubroutine, self).__init__()
		self._stop = threading.Event()
		self.stopEventHandle = kwargs.pop('stopHandle', None)
		self.target = target
		self.args   = args
		self.kwargs = kwargs
	
	def run(self):
		self.target(*self.args, **self.kwargs)

	def stop(self):
		self._stop.set()
		if(self.stopEventHandle!=None):
			self.stopEventHandle()

	def stopped(self):
		return self._stop.isSet()
	
if __name__ == '__main__':
	while True:
		try:
			print "Please input number: (1 for server)"
			opt = int(stdin.readline())
			break
		except:
			pass
	p = P2Pconnection()
	if(opt==1):
		p.accept()
		obj = p.recv()
		obj.cal() 
	else:
		while True:
			try:
				addr = Address()
				addr.getInput()
				p.connect(addr)
				p.send(TestData(123,456))
				break
			except Exception as e:
				print str(e)