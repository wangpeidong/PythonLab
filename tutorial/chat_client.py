import socket

import logging
from chat_bot import ClientChatBot, PORT

def error_callback(error):
	logging.error(f'encountered error: {error}')

def incoming_callback(username, message):
	logging.info(f'received message: {message} from user: {username}')

def run_chat_bot(chat_bot):
	username = None
	# Connect with username first
	def connect():
		run_chat_bot.username = input('Username: ')
		if run_chat_bot.username:
			return chat_bot.connect(socket.gethostname(), PORT, run_chat_bot.username, error_callback)
		return False

	def chat():
		while True:
			message = input(f'{run_chat_bot.username} > ')
			if not message:
				break
			chat_bot.send(message)

	if not connect(): 
		return

	# Spawn a thread to listen for incoming message
	chat_bot.start_listening(incoming_callback, error_callback)

	chat()

	logging.info(f'chat ended')

if __name__ == '__main__':
	try:
		chat_bot = ClientChatBot(logging.INFO)
		run_chat_bot(chat_bot)
	except Exception as e:
		logging.warning(f'[main] exception: {str(e)}')
	finally:
		if chat_bot.client_socket is not None:
			chat_bot.client_socket.close()
			logging.info('socket closed')

