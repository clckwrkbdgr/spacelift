import operator, math
import base

PLATFORM_SIZE = 50, 60
PLATFORM_HP = 100
PLATFORM_DAMAGE = 65535
ENEMY_HP = 30
ENEMY_DAMAGE = 30
ENEMY_SIZE = 40, 50
ENEMY_SPEED = 0.0
WALL_SIZE = 50, base.SCREEN_SIZE[1]
BULLET_SIZE = 10, 10
BULLET_SPEED = 2
BULLET_DAMAGE = 10
PLAYER_SHOOTING_DELAY = 100
ENEMY_SHOOTING_DELAY = 1000
START_POS = 320, 420
BONUS_SIZE = 32, 32
HEALTH_BONUS_INC = 30
INVULNERABILITY_TIME = 2000

class PlayerBullet(base.Object):
	def __init__(self, pos):
		base.Object.__init__(self, pos, BULLET_SIZE, base.BLUE)
		self.speed = (0, -BULLET_SPEED)

	def collide_with(self, other):
		if isinstance(other, Enemy):
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
		if isinstance(other, Enemy):
			if self.invulnerability <= 0:
				self.hp -= ENEMY_DAMAGE
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

class Enemy(base.Object):
	def __init__(self, pos):
		base.Object.__init__(self, pos, ENEMY_SIZE, base.RED)
		self.weapon = base.Weapon(ENEMY_SHOOTING_DELAY, EnemyBullet)
		self.max_hp = ENEMY_HP
		self.hp = self.max_hp

	def collide_with(self, other):
		if isinstance(other, Platform):
			self.hp -= PLATFORM_DAMAGE
		elif isinstance(other, PlayerBullet):
			self.hp -= BULLET_DAMAGE
		if self.hp <= 0:
			self.alive = False

	def action(self):
		self.pos[1] += base.LEVEL_SPEED + ENEMY_SPEED
		return self.weapon.shoot(self.pos)

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


