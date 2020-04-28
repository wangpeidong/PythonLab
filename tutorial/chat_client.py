import socket
import select 
import errno
import sys

import logging
import time
from chat_bot import ChatBot, PORT

import multiprocessing

def listener_bot(chat_bot, client_socket):
	print(f'starting listener bot ...')
	logging.info(f'starting listener bot ...')
	while True:
		message = chat_bot.recv_message(client_socket)
		if message is None: break
		print(f'received message header: {message["header"]} body: {message["body"]}')
		logging.info(f'received message header: {message["header"]} body: {message["body"]}')

def spawn_listener():
	process = multiprocessing.Process(target = listener_bot, args = (chat_bot, client_socket))
	process.start()
	return process

def run_chat_bot():

	def logon_new_user():
		username = input('Username: ')
		if username:
			chat_bot.send_message(client_socket, username)
			return username
		return None

	def chat(username):
		message = input(f'{username} > ')
		if message:
			chat_bot.send_message(client_socket, message)
			return True
		return False

	client_socket.connect((socket.gethostname(), PORT))

	username = logon_new_user()
	if username is None: return

	while chat(username):
		pass

	logging.info(f'chat ended')

if __name__ == '__main__':
	try:
		chat_bot = ChatBot(logging.INFO)
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		process = spawn_listener()
		run_chat_bot()
	except Exception as e:
		logging.warning(f'Exception: {str(e)}')
	finally:
		client_socket.shutdown(socket.SHUT_WR) # Required for multiprocessing
		client_socket.close()
		logging.info('socket closed')
		process.terminate()
		logging.info('listener terminated')

