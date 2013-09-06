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

# TYPE             = PARTY                SIZE           COLOR   MAX_HP       DAMAGE           SPEED                           SHOOTING DELAY         BULLET_TYPE
BONUS_TYPE         = BONUS_PARTY,         BONUS_SIZE   , YELLOW, 1,           0,               (0, LEVEL_SPEED),               None,                  None
PLAYER_BULLET_TYPE = PLAYER_BULLET_PARTY, BULLET_SIZE  , BLUE  , 1,           BULLET_DAMAGE,   (0, -BULLET_SPEED),             None,                  None
ENEMY_BULLET_TYPE  = ENEMY_BULLET_PARTY,  BULLET_SIZE  , RED   , 1,           BULLET_DAMAGE,   (0, BULLET_SPEED),              None,                  None
PLATFORM_TYPE      = PLAYER_PARTY,        PLATFORM_SIZE, BLUE  , PLATFORM_HP, PLATFORM_DAMAGE, (0, 0),                         PLAYER_SHOOTING_DELAY, PLAYER_BULLET_TYPE
ENEMY_TYPE         = ENEMY_PARTY,         ENEMY_SIZE   , RED   , ENEMY_HP,    ENEMY_DAMAGE,    (0, ENEMY_SPEED + LEVEL_SPEED), ENEMY_SHOOTING_DELAY,  ENEMY_BULLET_TYPE

class Object:
	def __init__(self, pos, type_values, controller=None):
		self.party, size, color, self.max_hp, self.damage, self.speed, self.max_shooting_delay, self.bullet_type = type_values
		self.controller = controller

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

class Player:
	def __init__(self, rects):
		self.rects = rects
		self.shift = (0, 0)
		self.shooting = False

	def move(self, o):
		o.move(self.shift, 0, self.rects)

	def shoot(self, o):
		return o.shoot(self.shooting)

class Enemy:
	def move(self, o):
		pass

	def shoot(self, o):
		return o.shoot(True)


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

level_map = []
level_map += [(ENEMY_TYPE, Enemy, i * 500, 100 + i * 25) for i in range(20)]
level_map += [(BONUS_TYPE, None, 100 + i * 1000, random.randrange(wall_left_rect.right + BONUS_SIZE[0]/2, wall_right_rect.left - BONUS_SIZE[0]/2)) for i in range(5)]

player = Player([wall_left_rect, wall_right_rect])

platform_count = 3
level_pos = 0
platform = Object(START_POS, PLATFORM_TYPE, player)
objects = [platform]

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			if event.key == K_q or event.key == K_ESCAPE:
				sys.exit()
	player.shift = pygame.mouse.get_rel()[0]
	player.shooting = any(pygame.mouse.get_pressed())

	# Logic.
	level_pos += LEVEL_SPEED

	for object_type, controller, map_pos, screen_pos in level_map:
		if map_pos < level_pos:
			objects.append(Object((screen_pos, 0), object_type, controller() if controller else None))
	level_map = [(object_type, controller, map_pos, screen_pos) for object_type, controller, map_pos, screen_pos in level_map if map_pos > level_pos]

	new_objects = []
	for o in objects:
		if o.controller:
			o.controller.move(o)
			new_objects += o.controller.shoot(o)
		o.auto_move()
	objects += new_objects

	for a in objects:
		for b in objects:
			if (a.party, b.party) in COLLIDES:
				if a.get_rect().colliderect(b.get_rect()):
					a.hp -= b.damage
					b.hp -= a.damage

	for o in objects:
		if o.max_hp > 0 and o.hp <= 0:
			o.alive = False

	objects = [o for o in objects if o.alive and 0 < o.get_rect().bottom and o.get_rect().top < SCREEN_SIZE[1]]
	if not platform.alive:
		platform_count -= 1
		platform = Object(START_POS, PLATFORM_TYPE, player)
		objects.append(platform)
		if platform_count < 0:
			sys.exit()

	# Drawing.
	screen.fill(BLACK)
	screen.blit(wall_left, wall_left_rect)
	screen.blit(wall_right, wall_right_rect)
	for o in objects:
		screen.blit(o.surface, o.get_rect())

	hud = ["Level: {0:10.2f}; x{2}, {1}".format(level_pos, "shooting" if player.shooting else "", platform_count)]
	for o in objects:
		hud.append("{0}: ({1:0.2f},{2:#0.2f}) {3}/{4}hp".format(o.party, o.pos[0], o.pos[1], o.hp, o.max_hp))
	for number, line in enumerate(hud):
		screen.blit(font.render(line, True, WHITE), (wall_left_rect.right, number * font.get_height()))

	pygame.display.flip()
