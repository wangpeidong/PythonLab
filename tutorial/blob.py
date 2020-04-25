import random
import numpy as np

WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Blob:

	def __init__(self, color):
		self.x = random.randrange(0, WIDTH)
		self.y = random.randrange(0, HEIGHT)
		self.size = random.randrange(4, 8)
		self.color = color

	def __add__(self, other):
		if self == other:
			pass
		elif self.color == other.color:
			self.size += other.size
			other.size = 0
		else:
			pass

	def collide(self, other):
		if self.size == 0 or other.size == 0:
			return False
		else:
			return np.linalg.norm(np.array([self.x, self.y]) - np.array([other.x, other.y])) < (self.size + other.size)

	def __str__(self):
		return f'Color: {self.color}, Size: {self.size}, Position: {self.x, self.y}'

	def __repr__(self):
		return f'Blob({self.color}, {self.size}, ({self.x, self.y})'

	def move(self):
		move_x = random.randrange(-2, 3)
		move_y = random.randrange(-2, 3)
		self.x += move_x
		self.y += move_y

		if self.x < 0: self.x = 0
		elif self.x > WIDTH: self.x = WIDTH

		if self.y < 0: self.y = 0
		elif self.y > HEIGHT: self.y = HEIGHT		

import itertools
import logging
def handle_collisions(blobs):
	swollowed_blobs = []
	for b1, b2 in itertools.combinations(blobs, 2):
		if b1.collide(b2):
			logging.debug(f'{b1} and {b2} collided')
			b1 + b2
			if b2.size == 0:
				logging.info(f'{b2} swallowed')
				swollowed_blobs.append(b2)

	return [blob for blob in blobs if blob not in swollowed_blobs]

