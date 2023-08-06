from perks.DEV import Mark
from threading import *
from socket import *
import subprocess

############################# CONNECTION CLASS ##############################

class Connection(metaclass=Mark):

	NOT_RESULTS = []
	RESULTS = []
	ScreenLock = Semaphore(1)

	@classmethod
	def _PortScan(cls, SvcHost, SvcPort):
		
		try:
			SvcScan = socket(AF_INET, SOCK_STREAM)
			SvcScan.connect((SvcHost, SvcPort))

			SvcScan.send('flag\t'.encode())
			flag_value = SvcScan.recv(500)

			cls.ScreenLock.acquire()
			cls.RESULTS.append(SvcPort)

		except:
			cls.ScreenLock.acquire()
			cls.NOT_RESULTS.append(SvcPort)
			
		finally:       
			cls.ScreenLock.release()
			SvcScan.close()

	@classmethod
	def _HostConnect(cls, TcpHost, TcpPort=None):
		try:
			tgtIP = gethostbyname(TcpHost)

		except:
			return False

		try:
			tgtName = gethostbyaddr(tgtIP)
			
		except:
			tgtName = tgtIP

		setdefaulttimeout(1)
		
		if TcpPort:
			for ServerPort in TcpPort:

				_thread = Thread(target=cls._PortScan, args=(TcpHost, int(ServerPort)))
				_thread.start()
		else:
			
			for ServerPort in range(1, 100):

				_thread = Thread(target=cls._PortScan, args=(TcpHost, int(ServerPort)))
				_thread.start()
				
		_thread.join()
		return None

	@classmethod
	def local_ip(cls, ipv6=False):

		def enm(lista):
			i = 0

			while True:
				yield (i, lista[i])
				i += 1

		import subprocess
		if ipv6:
			_data = subprocess.run('ipconfig', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			_data = str(_data.stdout) + str(_data.stderr)
			_data = _data.replace('\\n','\n').replace('\\t', '\t').replace('\\r','\r').replace('\\\\', '\\')

			for pos, val in enm(_data.split()):
				if val.lower().startswith('ipv6'):
					for vax in _data.split()[pos:]:
						if ':' in vax and (not vax.strip() == ':'):
							return vax
			else:
				return False

		else:
			_data = subprocess.run('ipconfig', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			_data = str(_data.stdout) + str(_data.stderr)
			_data = _data.replace('\\n','\n').replace('\\t', '\t').replace('\\r','\r').replace('\\\\', '\\')

			for pos, val in enm(_data.split()):
				if val.lower().startswith('ipv4'):
					for vax in _data.split()[pos:]:
						if vax.startswith('1'):
							return vax
			else:
				return False

	@classmethod
	def get_ip(cls):
		try:
			return str(gethostbyname(gethostname()))

		except:
			return False

	@classmethod
	def Scan(cls, Host, Port, complete_result=False):
		
		if isinstance(Port, str):
			TargetPort = list(Port.split(","))
			
		elif isinstance(Port, (tuple,list,set,frozenset)):
			TargetPort = list(Port)

		else:
			raise ValueError("Ports must be in a tuple, or separated by commas in a string.")

		try:
			if complete_result:
				cls._HostConnect(Host, TargetPort)
				return (cls.RESULTS, cls.NOT_RESULTS)

			else:
				cls._HostConnect(Host, TargetPort)
				return cls.RESULTS

		except:
			return False

	@classmethod
	def scan(cls, Host, port):
		try:
			lonley_port = []
			lonley_port.append(port)
			
			cls._HostConnect(Host, lonley_port)
			if not cls.RESULTS:
				return False
			else:
				return True
		except:
			return None


	@classmethod
	def Server(cls, funct):     
		"""
		Port -> One   : 15000
				Two   : 15600
				Three : 36000
				Four  : 41000
		"""
		def wrap():
			try:
				cls.Stable_Server(15000, func=funct)
				return True
			except:    
				try:
					cls.Stable_Server(16000, func=funct)
				except:
					try:
						cls.Stable_Server(36000, func=funct)
					except:
						try:
							cls.Stable_Server(41000, func=funct)
						except:
							return False
		return wrap

	@classmethod
	def Stable_Server(cls, port, func=None, address='', backlog=3, buffer=4096, listener=1, stop_keyword='Server --kill'):

		if backlog == 0 or backlog > 200:
			return False

		try:
			NO_USE = subprocess.run('chcp 65001', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			
		except:
			pass

		_LISTENER = int(listener)
		_BUFFER = int(buffer)
		_BACKLOG = int(backlog)
		_HOST = str(address)
		_FUNC = func
		_PORT = int(port)

		try:
			socket_server = socket()
			socket_server.bind((_HOST,_PORT))
			socket_server.listen(_LISTENER)

		except error as sk_error:
			cls.Stable_Server(_PORT, backlog=(_BACKLOG-1))

		try:
			while True:
				CONNECTION, (client_IP, client_PORT) = socket_server.accept()

				try:
					
					while True:
						try:

							_recieveData = CONNECTION.recv(_BUFFER).decode()
							
							if _recieveData.lower() == stop_keyword:
								return None

							if func:
								response = _FUNC(str(_recieveData))
							else:
								response = cls.Server_RESPONSE_NULL(str(_recieveData))

							response = str(response)
							response = response.encode()
						  
							CONNECTION.send(response)
						except:
						
							CONNECTION.send('Flag Error :: Server-Failed-Queue'.encode())
				except:
					pass
								
				finally:
					CONNECTION.close()

		finally:
		
			socket_server.close()
			return None

	@classmethod
	def Server_RESPONSE_NULL(cls, data):
		return data

	@classmethod
	def Connect(cls, host, port, buffer=4096, stop_keyword='Client --kill'):
		try:
			NO_RES = subprocess.run("chcp 65001", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		except:
			 pass

		_HOST = host
		_PORT = port
		_BUFFER = buffer

		socket_backdoor = socket()
		socket_backdoor.connect((_HOST, _PORT))

		try:

			while True:
				command = input('>>>')

				if command.lower() == stop_keyword:
					break
				
				socket_backdoor.send(command.encode())

				data = socket_backdoor.recv(_BUFFER).decode()
				print(data)
			return None
		
		finally:
			socket_backdoor.close()
			return None
			

	@classmethod
	def Exclusive_Server(cls, port, func=None, address='', _backlog=3, buffer=4096, listener=1):

		if _backlog == 0 or _backlog > 200:
			return False

		try:
			socket_server = socket()
			socket_server.bind((address,port))
			socket_server.listen(listener)

		except error as sk_error:
			cls.Stable_Server(port, _backlog=(_backlog-1))

		connection, (client_IP, client_PORT) = socket_server.accept()

		try:

			while True:
				try:

					_recieveData = connection.recv(buffer).decode()

					if func:
						response = func(str(_recieveData))
					else:
						response = cls.Server_RESPONSE_NULL(str(_recieveData))

					response = str(response)
					response = response.encode()

					connection.send(response)

				except:
					connection.send('Flag Error :: Server-Failed-Queue'.encode())

		finally:
			
			connection.close()
			socket_server.close()
			return None
			

	@classmethod
	def Altern_Server(cls, port, func, address='', _backlog=3, buffer=4096, listener=1):
		
		if _backlog == 0 or _backlog > 500:
			return False

		while True:
			
			try:
				s = socket()
				s.bind((address,port))
				s.listen(listener)
				
			except error as sk_error:
				cls.Server_Altern(port, func, _backlog=(_backlog-1))

			connection, client_address = s.accept()

			try:
				try:
					_queue = connection.recv(buffer).decode()
					res = func(str(_queue))
					
					res = str(res)
					res = res.encode()
					
					connection.send(res)
					connection.close()
				except:
					connection.send('Flag Error :: Server-Failed-Queue'.encode())
					connection.close()
					
			except:
				pass

		s.close()
		return True

	@classmethod
	def Altern_Connection(cls, address, command, buffer=4096):
		
		try:
			s = socket()
			s.connect(address)
		except error as sk_error:
			return False

		try:
			command = str(command)
			command = command.encode()
			s.send(command)
			data = s.recv(buffer)
			s.close()
			return data.decode()
			
		except error as sk_error:
			raise sk_error
 
