#!/usr/bin/python3
import sys
import pygame
from pygame.locals import *

BLACK = 0, 0, 0
RED = 255, 0, 0

SCREEN_MODE = 640, 480
PLATFORM_SIZE = 50, 60
START_POS = 320, 420

pygame.init()
screen = pygame.display.set_mode(SCREEN_MODE)
pygame.mouse.set_visible(False)
#pygame.mouse.set_pos(START_POS)
pygame.event.set_grab(True)

platform = pygame.surface.Surface(PLATFORM_SIZE)
platform.fill(RED)
platform_rect = platform.get_rect()
platform_rect.center = START_POS

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			if event.key == K_q:
				sys.exit()
	shift = pygame.mouse.get_rel()[0]

	# Logic.
	platform_rect.move_ip(shift, 0)

	# Drawing.
	screen.fill(BLACK)
	screen.blit(platform, platform_rect)

	pygame.display.flip()
