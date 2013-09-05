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
PLATFORM_DAMAGE = 65535
ENEMY_HP = 30
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

ENEMY_PARTY = "Enemy"
ENEMY_BULLET_PARTY = "Enemy bullet"
PLAYER_BULLET_PARTY = "Player bullet"
PLAYER_PARTY = "Player"
BONUS_PARTY = "Bonus"
COLLIDES = []
COLLIDES.append((ENEMY_PARTY, PLAYER_BULLET_PARTY))
COLLIDES.append((ENEMY_PARTY, PLAYER_PARTY))
COLLIDES.append((ENEMY_BULLET_PARTY, PLAYER_PARTY))
COLLIDES.append((BONUS_PARTY, PLAYER_PARTY))
collides = lambda a, b: ((a, b) in COLLIDES) or ((b, a) in COLLIDES) # TODO check if works

# TYPE             = PARTY                SIZE           COLOR   MAX_HP       DAMAGE           SPEED                           SHOOTING DELAY         BULLET_TYPE
BONUS_TYPE         = BONUS_PARTY,         BONUS_SIZE   , YELLOW, 1,           0,               (0, LEVEL_SPEED),               None,                  None
PLAYER_BULLET_TYPE = PLAYER_BULLET_PARTY, BULLET_SIZE  , BLUE  , 1,           BULLET_DAMAGE,   (0, -BULLET_SPEED),             None,                  None
ENEMY_BULLET_TYPE  = ENEMY_BULLET_PARTY,  BULLET_SIZE  , RED   , 1,           BULLET_DAMAGE,   (0, BULLET_SPEED),              None,                  None
PLATFORM_TYPE      = PLAYER_PARTY,        PLATFORM_SIZE, BLUE  , PLATFORM_HP, PLATFORM_DAMAGE, (0, 0),                         PLAYER_SHOOTING_DELAY, PLAYER_BULLET_TYPE
ENEMY_TYPE         = ENEMY_PARTY,         ENEMY_SIZE   , RED   , ENEMY_HP,    ENEMY_DAMAGE,    (0, ENEMY_SPEED + LEVEL_SPEED), ENEMY_SHOOTING_DELAY,  ENEMY_BULLET_TYPE

class Object:
	def __init__(self, pos, type_values):
		self.party, size, color, self.max_hp, self.damage, self.speed, self.max_shooting_delay, self.bullet_type = type_values

		self.surface = pygame.surface.Surface(size)
		self.surface.fill(color)

		self.pos = [float(x) for x in pos[:2]]
		self.alive = True
		self.hp = self.max_hp
		self.shooting_delay = 0

	def shoot(self, shooting):
		bullets = []
		if shooting and self.shooting_delay <= 0:
			bullets.append(Object(self.pos, self.bullet_type))
			self.shooting_delay = self.max_shooting_delay
		if self.shooting_delay > 0:
			self.shooting_delay -= 1
		return bullets

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

enemy_map = [(i * 500, 100 + i * 25) for i in range(20)]
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
	for o in player_bullets + enemy_bullets + bonuses + enemies:
		o.auto_move()

	for enemy in enemies:
		enemy_bullets += enemy.shoot(True)
	player_bullets += platform.shoot(shooting)

	for a in [platform] + enemies + player_bullets + enemy_bullets + bonuses:
		for b in [platform] + enemies + player_bullets + enemy_bullets + bonuses:
			if collides(a.party, b.party):
				if a.get_rect().colliderect(b.get_rect()):
					a.hp -= b.damage
					b.hp -= a.damage

	for o in [platform] + enemies + player_bullets + enemy_bullets + bonuses:
		if o.max_hp > 0 and o.hp <= 0:
			o.alive = False

	enemies = [enemy for enemy in enemies if enemy.alive and enemy.get_rect().top < SCREEN_SIZE[1]]
	player_bullets = [bullet for bullet in player_bullets if bullet.alive and 0 < bullet.get_rect().bottom]
	enemy_bullets = [bullet for bullet in enemy_bullets if bullet.alive and bullet.get_rect().top < SCREEN_SIZE[1]]
	bonuses = [bonus for bonus in bonuses if bonus.alive and bonus.get_rect().top < SCREEN_SIZE[1]]
	if not platform.alive:
		platform_count -= 1
		platform = Object(START_POS, PLATFORM_TYPE)
		if platform_count < 0:
			sys.exit()

	# Drawing.
	screen.fill(BLACK)
	screen.blit(wall_left, wall_left_rect)
	screen.blit(wall_right, wall_right_rect)
	for o in [platform] + bonuses + enemies + enemy_bullets + player_bullets:
		screen.blit(o.surface, o.get_rect())

	hud = ["Level: {0:10.2f}; x{2}, {1}".format(level_pos, "shooting" if shooting else "", platform_count)]
	for o in [platform] + bonuses + enemies + enemy_bullets + player_bullets:
		hud.append("{0}: ({1:0.2f},{2:#0.2f}) {3}/{4}hp".format(o.party, o.pos[0], o.pos[1], o.hp, o.max_hp))
	for number, line in enumerate(hud):
		screen.blit(font.render(line, True, WHITE), (wall_left_rect.right, number * font.get_height()))

	pygame.display.flip()
