
import logging
def set_logging(level):
	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(level)

	#file_handler = logging.FileHandler('logs/chat_bot.log')
	#file_handler.setLevel(logging.DEBUG)

	logging.basicConfig(
		level = logging.DEBUG,
		format = '%(asctime)s [%(levelname)s] %(message)s',
		handlers = [
			stream_handler,
			#file_handle
		]
	)

import pickle
HEADER_SIZE = 10
BUFFER_SIZE = 16
PORT = 1234

class ChatBot():
	def __init__(self, logging_level = logging.INFO):
		set_logging(logging_level)

	def header(self, msg):
		return f'{len(msg):<{HEADER_SIZE}}'

	def read_header(self, sckt):
		msg = sckt.recv(HEADER_SIZE)
		if len(msg) <= 0: return 0
		msg = msg.decode('utf-8').strip()
		msg_size = int(msg)
		logging.debug(f'message size: [{msg_size}]')
		return msg_size

	def read_body(self, sckt, len):
		if len <= 0: return
		cnt = 0
		full_msg = b''
		size = min(BUFFER_SIZE, len)
		while cnt < len:
			msg = sckt.recv(size)
			logging.debug(f'buffered message: [{msg}]')
			cnt += BUFFER_SIZE
			full_msg += msg
			size = min(BUFFER_SIZE, len - cnt)
		full_msg = pickle.loads(full_msg)
		logging.debug(f'full message: {full_msg}')	
		return full_msg

	def send_message(self, sckt, msg):
		msg = pickle.dumps(msg)
		msg = bytes(self.header(msg), 'utf-8') + msg
		logging.debug(msg)
		sckt.send(msg)

	def recv_message(self, sckt):
		try:
			msg_size = self.read_header(sckt)
			if msg_size == 0: 
				return None
			body = self.read_body(sckt, msg_size)
			return {'header': msg_size, 'body': body}
		except Exception as e:
			logging.warning(f'[recv_message] exception: {str(e)}')

		return None

import socket
from threading import Thread	

class ClientChatBot(ChatBot):
	client_socket = None

	def connect(self, ip, port, username, error_calllback):
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			self.client_socket.connect((ip, port))
		except Exception as e:
			error_calllback(f'[connect] error: {str(e)}')
			return False

		super().send_message(self.client_socket, username)
		return True

	def send(self, message):
		super().send_message(self.client_socket, message)

	def listen(self, incoming_callback, error_calllback):
		try:
			while True:
				# Retrieve username first
				username = super().recv_message(self.client_socket)
				if username is None:
					error_calllback(f'[listen] username is None, connection closed by the server')
					break
				# Retrieve message sent from the user
				message = super().recv_message(self.client_socket)
				if message is None:
					error_calllback(f'[listen] message is None, connection closed by the server')
					break
				incoming_callback(username['body'], message['body'])
		except Exception as e:
			error_calllback(f'[listen] error: {str(e)}')

	def start_listening(self, incoming_callback, error_calllback):
		Thread(target = self.listen, args = (incoming_callback, error_calllback), daemon = True).start()

import select
class ServerChatBot(ChatBot):
	server_socket = None
	sockets = []
	clients = {}

	def accept_connection(self):
		client_socket, client_address = self.server_socket.accept()
		user = super().recv_message(client_socket)
		if user is None: return 
		username = user['body']
		self.sockets.append(client_socket)
		self.clients[client_socket] = username
		logging.info(f'accepted connection from address: {client_address}, username: {username}')

	def receive(self, notified_socket):
		message = super().recv_message(notified_socket)
		if message is None:
			logging.info(f'connection closed from {self.clients[notified_socket]}')
			self.sockets.remove(notified_socket)
			del self.clients[notified_socket]
			return None
		username = self.clients[notified_socket]
		logging.info(f'received message from {username} - header: {message["header"]} body: {message["body"]}')
		return message['body']

	def broadcast(self, notified_socket, message):
		if not message:
			return

		for client_socket in self.clients:
			if client_socket != notified_socket:
				super().send_message(client_socket, self.clients[notified_socket])
				super().send_message(client_socket, message)
				logging.info(f'forwarded message: {message} from user: {self.clients[notified_socket]} to user: {self.clients[client_socket]}')

	def start_service(self, ip, port, error_calllback):
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.bind((ip, port))

		self.sockets.append(self.server_socket)

		self.server_socket.listen()
		logging.info(f'ServerChatBot listening on {ip}:{port} ...')

		try:
			while True:
				read_sockets, _, exception_sockets = select.select(self.sockets, [], self.sockets, 60)

				# Any client socket connects to server socket the very 1st time,
				# server then allocates a dedicated notification socket for following
				# communication.
				for notified_socket in read_sockets:
					if notified_socket == self.server_socket:
						self.accept_connection()
					else:
						self.broadcast(notified_socket, self.receive(notified_socket))

				for notified_socket in exception_sockets:
					self.sockets.remove(notified_socket)
					del self.clients[notified_socket]
		except Exception as e:
				error_calllback(f'[start_service] error: {str(e)}')


