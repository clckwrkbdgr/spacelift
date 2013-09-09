import pygame

BLACK = 0, 0, 0
BLUE = 0, 0, 255
GRAY = 80, 80, 80
WHITE = 255, 255, 255
RED = 255, 0, 0
YELLOW = 255, 255, 0
DARKGREEN = 0, 128, 0
GREEN = 0, 255, 0
PURPLE = 255, 0, 255

SCREEN_SIZE = 640, 480
LEVEL_SPEED = 0.3

class Object:
	def __init__(self, pos, size, color):
		self.surface = pygame.surface.Surface(size)
		self.surface.fill(color)
		self.pos = list(pos)
		self.alive = True

	def action(self):
		return []

	def collide_with(self, other):
		pass

	def get_rect(self):
		rect = self.surface.get_rect()
		rect.center = tuple(map(int, self.pos))
		return rect

class Weapon:
	def __init__(self, delay, bullet_type):
		self.max_delay = delay
		self.delay = 0
		self.bullet_type = bullet_type

	def shoot(self, pos, wants_to_shoot=True):
		bullets = []
		if wants_to_shoot and self.delay <= 0:
			bullets.append(self.bullet_type(pos))
			self.delay = self.max_delay
		if self.delay > 0:
			self.delay -= 1
		return bullets

class PlayerController:
	def __init__(self, rects):
		self.rects = rects
		self.shift = 0
		self.shooting = False

