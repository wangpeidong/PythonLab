import pygame
from blob import *

class RedBlob(Blob):
	def __init__(self):
		super().__init__(RED)

class GreenBlob(Blob):
	def __init__(self):
		super().__init__(GREEN)

class BlueBlob(Blob):
	def __init__(self):
		super().__init__(BLUE)


game_display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Blob World')
clock = pygame.time.Clock()

def draw_environment(blobs):
	game_display.fill(WHITE)
	for blob in blobs:
		pygame.draw.circle(game_display, blob.color, [blob.x, blob.y], blob.size)
	pygame.display.update()
    
STARTING_RED_BLOBS = 3
STARTING_GREEN_BLOBS = 5
STARTING_BLUE_BLOBS = 10
def main():
	blobs = [RedBlob() for _ in range(STARTING_RED_BLOBS)]
	[blobs.append(GreenBlob()) for _ in range(STARTING_GREEN_BLOBS)]
	[blobs.append(BlueBlob()) for _ in range(STARTING_BLUE_BLOBS)]

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

		draw_environment(blobs)
		blobs = handle_collisions(blobs)
		for blob in blobs: blob.move()
		clock.tick(60)

if __name__ == '__main__':
	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(logging.INFO)

	file_handler = logging.FileHandler('debug.log')
	file_handler.setLevel(logging.DEBUG)

	logging.basicConfig(
		level = logging.DEBUG,
		format = '%(asctime)s [%(levelname)s] %(message)s',
		handlers = [
			stream_handler,
			file_handler
		]
	)

	main()
    
