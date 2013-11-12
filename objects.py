import operator, math, random
import base

PLATFORM_SIZE = 50, 60
PLATFORM_HP = 100
PLATFORM_DAMAGE = 65535
TURRET_HP = 30
TURRET_DAMAGE = 30
TURRET_SIZE = 40, 50
WALL_SIZE = 50, base.SCREEN_SIZE[1]
BULLET_SIZE = 10, 10
BULLET_SPEED = 2
BULLET_DAMAGE = 10
PLAYER_SHOOTING_DELAY = 100
TURRET_SHOOTING_DELAY = 1000
START_POS = 320, 420
BONUS_SIZE = 32, 32
HEALTH_BONUS_INC = 30
INVULNERABILITY_TIME = 2000
BOMB_SIZE = 30, 30
BOMB_HP = 20
BOMB_SPEED = 1

class PlayerBullet(base.Object):
	def __init__(self, pos):
		base.Object.__init__(self, pos, BULLET_SIZE, base.BLUE)
		self.speed = (0, -BULLET_SPEED)

	def collide_with(self, other):
		if isinstance(other, Turret) or isinstance(other, Bomb):
			self.alive = False

	def action(self):
		self.pos = list(map(operator.add, self.pos, self.speed))
		return []

class PlayerLeftSideBullet(PlayerBullet):
	def __init__(self, pos):
		PlayerBullet.__init__(self, pos)
		speed = BULLET_SPEED / math.sqrt(2)
		self.speed = (-speed, -speed)

class PlayerRightSideBullet(PlayerBullet):
	def __init__(self, pos):
		PlayerBullet.__init__(self, pos)
		speed = BULLET_SPEED / math.sqrt(2)
		self.speed = (+speed, -speed)

class EnemyBullet(base.Object):
	def __init__(self, pos):
		base.Object.__init__(self, pos, BULLET_SIZE, base.RED)

	def collide_with(self, other):
		if isinstance(other, Platform):
			self.alive = False

	def action(self):
		self.pos[1] += BULLET_SPEED
		return []

class Platform(base.Object):
	def __init__(self, pos, controller):
		base.Object.__init__(self, pos, PLATFORM_SIZE, base.BLUE)
		self.weapons = [((0, 0), base.Weapon(PLAYER_SHOOTING_DELAY, PlayerBullet))]
		self.controller = controller
		self.max_hp = PLATFORM_HP
		self.hp = self.max_hp
		self.invulnerability = 0

	def collide_with(self, other):
		if isinstance(other, Turret) or isinstance(other, Bomb):
			if self.invulnerability <= 0:
				self.hp -= TURRET_DAMAGE
		elif isinstance(other, EnemyBullet):
			if self.invulnerability <= 0:
				self.hp -= BULLET_DAMAGE
		elif isinstance(other, WeaponBonus):
			if len(self.weapons) == 1:
				self.weapons.append( ((-PLATFORM_SIZE[0]/2, 0), base.Weapon(PLAYER_SHOOTING_DELAY, PlayerBullet)) )
				self.weapons.append( ((+PLATFORM_SIZE[0]/2, 0), base.Weapon(PLAYER_SHOOTING_DELAY, PlayerBullet)) )
			elif len(self.weapons) == 3:
				self.weapons.append( ((-PLATFORM_SIZE[0]/2, 0), base.Weapon(PLAYER_SHOOTING_DELAY, PlayerLeftSideBullet)) )
				self.weapons.append( ((+PLATFORM_SIZE[0]/2, 0), base.Weapon(PLAYER_SHOOTING_DELAY, PlayerRightSideBullet)) )
		elif isinstance(other, HealthBonus):
			self.hp += HEALTH_BONUS_INC
			if self.hp > self.max_hp:
				self.hp = self.max_hp
		elif isinstance(other, InvulnerabilityBonus):
			self.invulnerability += INVULNERABILITY_TIME
		if self.hp <= 0:
			self.alive = False

	def action(self):
		old_pos = self.pos[0]
		self.pos[0] += self.controller.shift
		if self.get_rect().collidelist(self.controller.rects) != -1:
			self.pos[0] = old_pos

		if self.invulnerability > 0:
			self.invulnerability -= 1

		bullets = []
		for shift, weapon in self.weapons:
			bullets += weapon.shoot(map(operator.add, self.pos, shift), self.controller.shooting)
		return bullets

class Turret(base.Object):
	def __init__(self, pos):
		base.Object.__init__(self, pos, TURRET_SIZE, base.RED)
		self.weapon = base.Weapon(TURRET_SHOOTING_DELAY, EnemyBullet)
		self.max_hp = TURRET_HP
		self.hp = self.max_hp

	def collide_with(self, other):
		if isinstance(other, Platform):
			self.hp -= PLATFORM_DAMAGE
		elif isinstance(other, PlayerBullet):
			self.hp -= BULLET_DAMAGE
		if self.hp <= 0:
			self.alive = False

	def action(self):
		self.pos[1] += base.LEVEL_SPEED
		return self.weapon.shoot(self.pos)

class Bomb(base.Object):
	def __init__(self, pos):
		base.Object.__init__(self, pos, BOMB_SIZE, base.RED)
		self.max_hp = BOMB_HP
		self.hp = self.max_hp

	def collide_with(self, other):
		if isinstance(other, Platform):
			self.hp -= PLATFORM_DAMAGE
		elif isinstance(other, PlayerBullet):
			self.hp -= BULLET_DAMAGE
		if self.hp <= 0:
			self.alive = False

	def action(self):
		self.pos[1] += base.LEVEL_SPEED + BOMB_SPEED
		return []

class Bonus(base.Object):
	def __init__(self, pos, color):
		base.Object.__init__(self, pos, BONUS_SIZE, color)

	def collide_with(self, other):
		if isinstance(other, Platform):
			self.alive = False

	def action(self):
		self.pos[1] += base.LEVEL_SPEED
		return []

class WeaponBonus(Bonus):
	def __init__(self, pos):
		base.Object.__init__(self, pos, BONUS_SIZE, base.YELLOW)

class HealthBonus(Bonus):
	def __init__(self, pos):
		base.Object.__init__(self, pos, BONUS_SIZE, base.DARKGREEN)

class InvulnerabilityBonus(Bonus):
	def __init__(self, pos):
		base.Object.__init__(self, pos, BONUS_SIZE, base.PURPLE)

class LevelMap:
	def __init__(self):
		self.level_map = []

	def random_pos(self, left, right, size):
		return random.randrange(left + size / 2, right - size / 2)

	def add_once(self, pos_func):
		pass

	def create(self, left, right):
		self.level_map += [(Turret, i * 500, 100 + i * 25) for i in range(20)]
		self.level_map += [(WeaponBonus, 100 + i * 1000, self.random_pos(left, right, BONUS_SIZE[0])) for i in range(5)]
		self.level_map += [(HealthBonus, 400 + i * 1000, self.random_pos(left, right, BONUS_SIZE[0])) for i in range(5)]
		self.level_map += [(InvulnerabilityBonus, 0, self.random_pos(left, right, BONUS_SIZE[0]))]

	def pull(self, level_pos):
		objects = []
		for object_type, map_pos, screen_pos in self.level_map:
			if map_pos < level_pos:
				objects.append(object_type((screen_pos, 0)))
		self.level_map = [(object_type, map_pos, screen_pos) for object_type, map_pos, screen_pos in self.level_map if map_pos > level_pos]
		return objects
