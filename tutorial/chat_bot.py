import pickle
import logging

HEADER_SIZE = 10
BUFFER_SIZE = 16
PORT = 1234

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
	multiprocessing_logging.install_mp_handler(logging.getLogger())

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
		logging.info(f'full message: {full_msg}')	
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
			logging.warning(f'Exception: {str(e)}')

		return None
