#!/usr/bin/python3
import sys, pygame, operator, random, math
from pygame.locals import *
import base, objects


pygame.init()
screen = pygame.display.set_mode(base.SCREEN_SIZE)
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
font = pygame.font.SysFont(None, 24)

wall_left = pygame.surface.Surface(objects.WALL_SIZE)
wall_left.fill(base.GRAY)
wall_left_rect = wall_left.get_rect()
wall_left_rect.topleft = 0, 0

wall_right = pygame.surface.Surface(objects.WALL_SIZE)
wall_right.fill(base.GRAY)
wall_right_rect = wall_right.get_rect()
wall_right_rect.topright = base.SCREEN_SIZE[0], 0

level_map = []
level_map += [(objects.Enemy, i * 500, 100 + i * 25) for i in range(20)]
level_map += [(objects.WeaponBonus, 100 + i * 1000, random.randrange(wall_left_rect.right + objects.BONUS_SIZE[0]/2, wall_right_rect.left - objects.BONUS_SIZE[0]/2)) for i in range(5)]
level_map += [(objects.HealthBonus, 400 + i * 1000, random.randrange(wall_left_rect.right + objects.BONUS_SIZE[0]/2, wall_right_rect.left - objects.BONUS_SIZE[0]/2)) for i in range(5)]
level_map += [(objects.InvulnerabilityBonus, 0, random.randrange(wall_left_rect.right + objects.BONUS_SIZE[0]/2, wall_right_rect.left - objects.BONUS_SIZE[0]/2))]

player = base.PlayerController([wall_left_rect, wall_right_rect])

platform_count = 3
level_pos = 0
platform = objects.Platform(objects.START_POS, player)
objects = [platform]
player.shift = pygame.mouse.get_rel()[0]

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
	level_pos += base.LEVEL_SPEED

	for object_type, map_pos, screen_pos in level_map:
		if map_pos < level_pos:
			objects.append(object_type((screen_pos, 0)))
	level_map = [(object_type, map_pos, screen_pos) for object_type, map_pos, screen_pos in level_map if map_pos > level_pos]

	new_objects = []
	for o in objects:
		new_objects += o.action()
	objects += new_objects

	for a in objects:
		for b in objects:
			if a.get_rect().colliderect(b.get_rect()):
				a.collide_with(b)

	objects = [o for o in objects if o.alive and 0 < o.get_rect().bottom and o.get_rect().top < base.SCREEN_SIZE[1]]
	if not platform.alive:
		platform_count -= 1
		platform = objects.Platform(objects.START_POS, player)
		objects.append(platform)
		if platform_count < 0:
			sys.exit()

	# Drawing.
	screen.fill(base.BLACK)
	screen.blit(wall_left, wall_left_rect)
	screen.blit(wall_right, wall_right_rect)
	for o in objects:
		screen.blit(o.surface, o.get_rect())

	hud = "Level: {0:10.2f}; {2}x {3}/{4}hp, {1}, inv: {5}".format(level_pos,
			"shooting" if player.shooting else "        ",
			platform_count, platform.hp, platform.max_hp,
			platform.invulnerability
			)
	hud = [hud]
	for o in objects:
		hud.append("{0}: ({1:0.2f},{2:#0.2f})".format(o.__class__.__name__, o.pos[0], o.pos[1]))
	for number, line in enumerate(hud):
		screen.blit(font.render(line, True, base.WHITE), (wall_left_rect.right, number * font.get_height()))

	pygame.display.flip()
