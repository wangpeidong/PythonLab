from colorama import Fore, Back, Style, init

def print_title(game):
	print("   " + "  ".join([str(i) for i in range(len(game))]))

def print_colored_row(idx, row):
	colored_row = ""
	for item in row:
		if item == 0: colored_row += " - "
		elif item == 1: colored_row += Fore.GREEN + " X " + Style.RESET_ALL
		elif item == 2: colored_row += Fore.MAGENTA + " O " + Style.RESET_ALL
	print(idx, colored_row)


def game_board(game, player = 0, row = 0, column = 0, just_display = False):
	if just_display == True:
		print_title(game)
		for idx, irow in enumerate(game): print_colored_row(idx, irow)
	else:
		try:
			if game[row][column] == 0:
				game[row][column] = player
			else:
				print(f"[{row}][{column}] already chosen, try another")
				return False
		except Exception as e:
			print(f"Exception: {str(e)}, try another")
			return False
	return True

def win(game):
	def all_same(check, msg = ""):
		if check.count(check[0]) == len(check) and check[0] != 0:
			print(f"Player {check[0]} is the winner {msg}")
			return True
		return False

	print_title(game)
	# horizontal
	for idx, row in enumerate(game):
		print_colored_row(idx, row)
		if all_same(row, "horizontally"):
			return True
	# vertical
	for col in range(len(game)):
		check = []
		for row in game:
			check.append(row[col])
		if all_same(check, "vertically"):
			return True
	# / diagonal
	diag = []
	size = range(len(game))
	for idx in size:
		diag.append(game[idx][size[-idx-1]])
	if all_same(diag, "diagonally /"):
		return True
	# \ diagonal
	diag = []
	for idx in range(len(game)):
		diag.append(game[idx][idx])
	if all_same(diag, "diagonally \\"):
		return True
	return False

import itertools
import random
def play_game():
	play = True
	players = [1, 2]
	game_size = 3
	while play:
		try:
			game_size = min(int(input("What size game TicTacToe (max 10) ? ")), 10)
		except ValueError:
			print(f"The size must be integer, default to {game_size}")
		game = [[0 for i in range(game_size)] for i in range(game_size)]

		game_won = False
		random.shuffle(players)
		player_cycle = itertools.cycle(players)
		current_player = next(player_cycle)
		pos_chosen = False
		game_board(game, just_display = True)
		while not game_won:
			print(f"Player: {current_player}")
			column_choice = int(input("Which column ? "))
			row_choice = int(input("Which row ? "))

			pos_chosen = game_board(game, current_player, row_choice, column_choice)
			if pos_chosen == True:
				game_won = win(game)
				current_player = next(player_cycle)

		if str(input("Do you want to play another game ? ")).lower() == 'n':
			play = False
			print(f"Byebye")
		else:
			print(f"Start a new game")

init()
play_game()
