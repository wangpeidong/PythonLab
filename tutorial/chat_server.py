import socket

import logging
from chat_bot import ServerChatBot, PORT

def error_callback(error):
	logging.error(f'encountered error: {error}')

if __name__ == '__main__':
	try:
		chat_bot = ServerChatBot(logging.INFO)
		chat_bot.start_service(socket.gethostname(), PORT, error_callback)
	except Exception as e:
		logging.warning(f'[main] exception: {str(e)}')
	finally:
		if chat_bot.server_socket is not None:
			chat_bot.server_socket.close()
			logging.info('socket closed')


