#!/usr/bin/python3
import sys
import pygame
import operator
from pygame.locals import *

BLACK = 0, 0, 0
BLUE = 0, 0, 255
GRAY = 80, 80, 80
WHITE = 255, 255, 255
RED = 255, 0, 0

SCREEN_SIZE = 640, 480
LEVEL_SPEED = 0.3
PLATFORM_SIZE = 50, 60
ENEMY_SIZE = 40, 50
ENEMY_SPEED = 0.0
WALL_SIZE = 50, SCREEN_SIZE[1]
START_POS = 320, 420

class Person:
	def __init__(self, size, color, pos):
		self.surface = pygame.surface.Surface(size)
		self.surface.fill(color)
		self.pos = [float(x) for x in pos[:2]]

	def move(self, x, y, rect_list=None):
		old_pos = self.pos
		self.pos = tuple(map(operator.add, map(float, self.pos), (x, y)))
		if rect_list is not None:
			if self.get_rect().collidelist(rect_list) != -1:
				self.pos = old_pos

	def get_rect(self):
		rect = self.surface.get_rect()
		rect.center = tuple(map(int, self.pos))
		return rect

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
font = pygame.font.SysFont(None, 24)

wall_left = pygame.surface.Surface(WALL_SIZE)
wall_left.fill(GRAY)
wall_left_rect = wall_left.get_rect()
wall_left_rect.topleft = 0, 0

wall_right = pygame.surface.Surface(WALL_SIZE)
wall_right.fill(GRAY)
wall_right_rect = wall_right.get_rect()
wall_right_rect.topright = SCREEN_SIZE[0], 0

platform = Person(PLATFORM_SIZE, BLUE, START_POS)
enemies = []
enemies.append(Person(ENEMY_SIZE, RED, (SCREEN_SIZE[0] / 2, 0)))

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			if event.key == K_q:
				sys.exit()
	shift = pygame.mouse.get_rel()[0]

	# Logic.
	platform.move(shift, 0, [wall_left_rect, wall_right_rect])
	for enemy in enemies:
		enemy.move(0, ENEMY_SPEED + LEVEL_SPEED)
	enemies = [enemy for enemy in enemies if enemy.get_rect().top < SCREEN_SIZE[1]]

	
	# Drawing.
	screen.fill(BLACK)
	screen.blit(platform.surface, platform.get_rect())
	screen.blit(wall_left, wall_left_rect)
	screen.blit(wall_right, wall_right_rect)
	for enemy in enemies:
		screen.blit(enemy.surface, enemy.get_rect())

	hud = [font.render("You: {0}, {1}".format(platform.pos[0], platform.pos[1]), True, WHITE)]
	for enemy in enemies:
		hud.append(font.render("Enemy: {0:10.2f}, {1:#10.2f}".format(enemy.pos[0], enemy.pos[1]), True, WHITE))
	for number, line in enumerate(hud):
		screen.blit(line, (wall_left_rect.right, number * font.get_height()))

	pygame.display.flip()
