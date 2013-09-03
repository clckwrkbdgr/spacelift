#!/usr/bin/python3
import sys
import pygame
import operator
import random
from pygame.locals import *

BLACK = 0, 0, 0
BLUE = 0, 0, 255
GRAY = 80, 80, 80
WHITE = 255, 255, 255
RED = 255, 0, 0
YELLOW = 255, 255, 0

SCREEN_SIZE = 640, 480
LEVEL_SPEED = 0.3
PLATFORM_SIZE = 50, 60
PLATFORM_HP = 100
ENEMY_HP = 10
ENEMY_DAMAGE = 30
ENEMY_SIZE = 40, 50
ENEMY_SPEED = 0.0
WALL_SIZE = 50, SCREEN_SIZE[1]
BULLET_SIZE = 10, 10
BULLET_SPEED = 2
BULLET_DAMAGE = 10
PLAYER_SHOOTING_DELAY = 100
ENEMY_SHOOTING_DELAY = 1000
START_POS = 320, 420
BONUS_SIZE = 32, 32

PLATFORM_TYPE = PLATFORM_SIZE, BLUE, PLATFORM_HP, (0, 0)
ENEMY_TYPE = ENEMY_SIZE, RED, ENEMY_HP, (0, ENEMY_SPEED + LEVEL_SPEED)
BONUS_TYPE = BONUS_SIZE, YELLOW, 0, (0, LEVEL_SPEED)
PLAYER_BULLET_TYPE = BULLET_SIZE, BLUE, 0, (0, -BULLET_SPEED)
ENEMY_BULLET_TYPE = BULLET_SIZE, RED, 0, (0, BULLET_SPEED)

class Object:
	def __init__(self, pos, type_values):
		size, color, self.max_hp, self.speed = type_values

		self.surface = pygame.surface.Surface(size)
		self.surface.fill(color)

		self.pos = [float(x) for x in pos[:2]]
		self.alive = True
		self.hp = self.max_hp
		self.shooting_delay = 0

	def move(self, x, y, rect_list=None):
		old_pos = self.pos
		self.pos = tuple(map(operator.add, map(float, self.pos), (x, y)))
		if rect_list is not None:
			if self.get_rect().collidelist(rect_list) != -1:
				self.pos = old_pos

	def auto_move(self):
		self.move(self.speed[0], self.speed[1])

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

enemy_map = [(i * 1000, 100 + i * 25) for i in range(20)]
bonus_map = [(100 + i * 1000, random.randrange(wall_left_rect.right + BONUS_SIZE[0]/2, wall_right_rect.left - BONUS_SIZE[0]/2)) for i in range(5)]

platform = Object(START_POS, PLATFORM_TYPE)
platform_count = 3
level_pos = 0
enemies = []
player_bullets = []
enemy_bullets = []
bonuses = []

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			if event.key == K_q or event.key == K_ESCAPE:
				sys.exit()
	shift = pygame.mouse.get_rel()[0]
	shooting = any(pygame.mouse.get_pressed())

	# Logic.
	level_pos += LEVEL_SPEED

	for map_pos, screen_pos in enemy_map:
		if map_pos < level_pos:
			enemies.append(Object((screen_pos, 0), ENEMY_TYPE))
	enemy_map = [(map_pos, screen_pos) for map_pos, screen_pos in enemy_map if map_pos > level_pos]

	for map_pos, screen_pos in bonus_map:
		if map_pos < level_pos:
			bonuses.append(Object((screen_pos, 0), BONUS_TYPE))
	bonus_map = [(map_pos, screen_pos) for map_pos, screen_pos in bonus_map if map_pos > level_pos]

	platform.move(shift, 0, [wall_left_rect, wall_right_rect])
	for bullet in player_bullets:
		bullet.auto_move()
	for bullet in enemy_bullets:
		bullet.auto_move()
	for bonus in bonuses:
		bonus.auto_move()
	for enemy in enemies:
		enemy.auto_move()

	for bullet in enemy_bullets:
		if platform.get_rect().colliderect(bullet.get_rect()):
			bullet.alive = False
			platform.hp -= BULLET_DAMAGE
	for enemy in enemies:
		for bullet in player_bullets:
			if enemy.get_rect().colliderect(bullet.get_rect()):
				bullet.alive = False
				enemy.hp -= BULLET_DAMAGE
	for enemy in enemies:
		if enemy.shooting_delay <= 0:
			enemy_bullets.append(Object(enemy.pos, ENEMY_BULLET_TYPE))
			enemy.shooting_delay = ENEMY_SHOOTING_DELAY
		if enemy.shooting_delay > 0:
			enemy.shooting_delay -= 1
	for enemy in enemies:
		if enemy.get_rect().colliderect(platform.get_rect()):
			enemy.alive = False
			platform.hp -= ENEMY_DAMAGE
	for enemy in enemies:
		if enemy.hp < 0:
			enemy.alive = False
	if shooting and platform.shooting_delay <= 0:
		player_bullets.append(Object(platform.pos, PLAYER_BULLET_TYPE))
		platform.shooting_delay = PLAYER_SHOOTING_DELAY
	if platform.shooting_delay > 0:
		platform.shooting_delay -= 1
	if platform.hp <= 0:
		platform_count -= 1
		platform = Object(START_POS, PLATFORM_TYPE)
		if platform_count < 0:
			sys.exit()

	enemies = [enemy for enemy in enemies if enemy.alive and enemy.get_rect().top < SCREEN_SIZE[1]]
	player_bullets = [bullet for bullet in player_bullets if bullet.alive and 0 < bullet.get_rect().bottom]
	enemy_bullets = [bullet for bullet in enemy_bullets if bullet.alive and bullet.get_rect().top < SCREEN_SIZE[1]]
	bonuses = [bonus for bonus in bonuses if bonus.alive and bonus.get_rect().top < SCREEN_SIZE[1]]

	# Drawing.
	screen.fill(BLACK)
	screen.blit(platform.surface, platform.get_rect())
	screen.blit(wall_left, wall_left_rect)
	screen.blit(wall_right, wall_right_rect)
	for bullet in player_bullets:
		screen.blit(bullet.surface, bullet.get_rect())
	for enemy in enemies:
		screen.blit(enemy.surface, enemy.get_rect())
	for bullet in enemy_bullets:
		screen.blit(bullet.surface, bullet.get_rect())
	for bonus in bonuses:
		screen.blit(bonus.surface, bonus.get_rect())

	hud = ["You: ({0:10.2f},{1:10.2f}) {2}/{3}hp x{4}".format(platform.pos[0], platform.pos[1], platform.hp, platform.max_hp, platform_count)]
	hud.append("Level: {0:10.2f}; {1}".format(level_pos, "shooting" if shooting else ""))
	for bonus in bonuses:
		hud.append("Bonus: {0:10.2f}, {1:#10.2f}".format(bonus.pos[0], bonus.pos[1]))
	for enemy in enemies:
		hud.append("Enemy: {0:10.2f}, {1:#10.2f}".format(enemy.pos[0], enemy.pos[1]))
	for bullet in enemy_bullets:
		hud.append("Bullet: {0:10.2f}, {1:#10.2f}".format(bullet.pos[0], bullet.pos[1]))
	for bullet in player_bullets:
		hud.append("Bullet: {0:10.2f}, {1:#10.2f}".format(bullet.pos[0], bullet.pos[1]))
	for number, line in enumerate(hud):
		screen.blit(font.render(line, True, WHITE), (wall_left_rect.right, number * font.get_height()))

	pygame.display.flip()
