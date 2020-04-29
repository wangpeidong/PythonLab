# Activate kivy virtual environment first, run below
# kivy_env>Scripts\activate
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock

import logging
import os, sys


from chat_bot import ClientChatBot

kivy.require("1.11.1")

class ConnectPage(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.cols = 2

		prev_ip = ''
		prev_port = ''
		prev_username = ''
		if os.path.isfile('prev_details.txt'):
			with open('prev_details.txt', 'r') as f:
				d = f.read().split(',')
				prev_ip = d[0]
				prev_port = d[1]
				prev_username = d[2]

		self.add_widget(Label(text = 'IP:'))
		self.ip = TextInput(text = prev_ip, multiline = False)
		self.add_widget(self.ip)

		self.add_widget(Label(text = 'Port:'))
		self.port = TextInput(text = prev_port, multiline = False)
		self.add_widget(self.port)

		self.add_widget(Label(text = 'Username:'))
		self.username = TextInput(text = prev_username, multiline = False)
		self.add_widget(self.username)

		self.join = Button(text = 'Join')
		self.join.bind(on_press = self.join_button)
		self.add_widget((Label())) # Just take up the space
		self.add_widget(self.join)
		
	def connect(self, _):
		port = int(self.port.text)
		ip = self.ip.text
		username = self.username.text

		chat_app.chat_bot = ClientChatBot()

		if not chat_app.chat_bot.connect(ip, port, username, show_error):
			return

		chat_app.create_chat_page()
		chat_app.screen_manager.current = 'Chat'

	def join_button(self, instance):
		port = self.port.text
		ip = self.ip.text
		username = self.username.text

		with open('prev_details.txt', 'w') as f:
			f.write(f'{ip},{port},{username}')

		info = f'Joining {ip}:{port} as {username}'
		my_logger.info(info)
		chat_app.info_page.update_info(info)
		chat_app.screen_manager.current = 'Info'

		Clock.schedule_once(self.connect, 1)

class InfoPage(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1
		self.message = Label(halign = 'center', valign = 'middle', font_size = 30)
		self.message.bind(width = self.update_text_width)
		self.add_widget(self.message)

	def update_info(self, message):
		self.message.text = message

	def update_text_width(self, *_):
		self.message.text_size = (self.message.width * 0.9, None)

from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
class ScrollableLabel(ScrollView):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.layout = GridLayout(cols = 1, size_hint_y = None)
		self.add_widget(self.layout)

		self.chat_history = Label(size_hint_y = None, markup = True)
		self.scroll_to_point = Label()

		self.layout.add_widget(self.chat_history)
		self.layout.add_widget(self.scroll_to_point)

	def update_chat_history(self, message):
		self.chat_history.text += '\n' + message

		self.update_chat_history_layout()

		self.scroll_to(self.scroll_to_point)

	def update_chat_history_layout(self, _ = None):
		self.layout.height = self.chat_history.texture_size[1] + 15
		self.chat_history.height = self.chat_history.texture_size[1]
		self.chat_history.text_size = (self.chat_history.width * 0.98, None)

class ChatPage(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.cols = 1
		self.rows = 2

		self.history = ScrollableLabel(height = Window.size[1] * 0.9, size_hint_y = None)
		self.add_widget(self.history)
		self.input = TextInput(width = Window.size[0] * 0.8, size_hint_x = None, multiline = False)
		self.send = Button(text = 'Send')
		self.send.bind(on_press = self.send_message)
		bottom_row = GridLayout(cols = 2)
		bottom_row.add_widget(self.input)
		bottom_row.add_widget(self.send)
		self.add_widget(bottom_row)

		self.bind(size = self.adjust_fields)

		Window.bind(on_key_down = self.on_key_down)

		Clock.schedule_once(self.focus_text_input, 1)

		chat_app.chat_bot.start_listening(self.incoming_message, show_error)

	def adjust_fields(self, *_):
		height = Window.size[1]
		if height * 0.1 < 50:
			new_height = height - 50
		else:
			new_height = height * 0.9
		self.history.height = new_height

		width = Window.size[0]
		if width * 0.2 < 160:
			new_width = width - 160
		else:
			new_width = width * 0.8
		self.input.width = new_width

		Clock.schedule_once(self.history.update_chat_history_layout, 0.01)

	def on_key_down(self, instance, keyboard, keycode, text, modifiers):
		if keycode == 40:
			self.send_message(None)

	def focus_text_input(self, _):
		self.input.focus = True

	def incoming_message(self, username, message):
		self.history.update_chat_history(f'[color=20dd20]{username}[/color] > {message}')

	def send_message(self, _):
		message = self.input.text
		self.input.text = ''

		if message:
			self.history.update_chat_history(f'[color=dd2020]{chat_app.connect_page.username.text}[/color] > {message}')
			chat_app.chat_bot.send(message)

		Clock.schedule_once(self.focus_text_input, 0.1)

from kivy.uix.screenmanager import ScreenManager, Screen
class ChatApp(App):
	chat_bot = None

	def build(self):
		self.screen_manager = ScreenManager()
		self.connect_page = ConnectPage()
		screen = Screen(name = 'Connect')
		screen.add_widget(self.connect_page)
		self.screen_manager.add_widget(screen)

		self.info_page = InfoPage()
		screen = Screen(name = 'Info')
		screen.add_widget(self.info_page)
		self.screen_manager.add_widget(screen)

		return self.screen_manager

	def create_chat_page(self):
		self.chat_page = ChatPage()
		screen = Screen(name = 'Chat')
		screen.add_widget(self.chat_page)
		self.screen_manager.add_widget(screen)

def show_error(message):
	my_logger.info(message)
	chat_app.info_page.update_info(message)
	chat_app.screen_manager.current = 'Info'

	if chat_app.chat_bot and chat_app.chat_bot.client_socket:
		chat_app.chat_bot.client_socket.close()

	Clock.schedule_once(sys.exit, 10)

def set_logging():
	formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt = '%Y-%m-%d %H:%M:%S')

	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(logging.INFO)
	stream_handler.setFormatter(formatter)

	file_handler = logging.FileHandler('logs/debug.log')
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(formatter)

	my_logger.addHandler(stream_handler)
	my_logger.addHandler(file_handler)
	my_logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
	my_logger = logging.getLogger('MyLogger')
	set_logging()
	chat_app = ChatApp()
	chat_app.run()

# Run below command to package to windows executable
#
# pyinstaller --hidden-import pkg_resources.py2_warn --name chatapp chatapp.py
#

# Then modify generated chatapp.spec file to add dependencies
# from kivy_deps import sdl2, glew
# and run below command again to build package 
#
# pyinstaller chatapp.spec
#
