import socket
import select

import logging

from chat_bot import ChatBot, PORT

def run_chat_bot(server_socket):
	def accept_new_user():
		client_socket, client_address = server_socket.accept()
		user = chat_bot.recv_message(client_socket)
		if user is None: return False
		username = user['body']
		sockets_list.append(client_socket)
		clients[client_socket] = username
		logging.info(f'accepted new connection from address: {client_address}, username: {username}')
		return True

	def receive_message(notified_socket):
		message = chat_bot.recv_message(notified_socket)
		if message is None:
			logging.info(f'connection closed from {clients[notified_socket]}')
			sockets_list.remove(notified_socket)
			del clients[notified_socket]
			return None
		username = clients[notified_socket]
		logging.info(f'received message from {username} - header: {message["header"]} body: {message["body"]}')
		return message['body']

	def broadcast_message(notified_socket, message):
		for client_socket in sockets_list:
			if client_socket != notified_socket and client_socket != server_socket:
				chat_bot.send_message(client_socket, message)
				logging.info(f'forwarded message: {message} to user: {clients[client_socket]}')

	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(((socket.gethostname(), PORT)))
	server_socket.settimeout(60)

	sockets_list = [server_socket]
	clients = {}

	chat_bot = ChatBot(logging.INFO)
	server_socket.listen()
	logging.info(f'ChatBot listening on {socket.gethostname()}:{PORT} ...')

	while True:
		read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list, 60)

		for notified_socket in read_sockets:
			if notified_socket == server_socket:
				if not accept_new_user(): continue
			else:
				message = receive_message(notified_socket)
				if message is None: continue
				broadcast_message(notified_socket, message)

		for notified_socket in exception_sockets:
			sockets_list.remove(notified_socket)
			del clients[notified_socket]

if __name__ == '__main__':
	try:
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		run_chat_bot(server_socket)
	except Exception as e:
		logging.warning(f'Exception: {str(e)}')
	finally:
		server_socket.shutdown(socket.SHUT_WR)
		server_socket.close()
		logging.info('socket closed')

