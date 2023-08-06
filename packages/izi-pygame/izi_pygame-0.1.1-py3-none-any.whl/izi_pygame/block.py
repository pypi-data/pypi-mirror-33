import pygame, pygame.mixer
from pygame.locals import*
import sys

class Block:
	"""
	Block -> hitbox no visible
	xbegin = xorigin of the block
	ybegin = yorigin of the block
	larg = width of the block
	haut = height of the block
	speed = the speed of the block if it moved
	id = the id of the block
	"""
	nb_block = 0
	list_block = []
	def __init__(self, x=0, y=0, larg=100, haut=100, speed=5):
		self.xbegin = x
		self.ybegin = y
		self.larg = larg
		self.haut = haut
		self.xend = x+larg
		self.yend = y+haut
		self.speed = speed
		self.id = Block.nb_block
		self.time = None
		Block.nb_block += 1
		Block.list_block.append(self)
	"""set the position of the block"""
	def set_position(self, x, y):
		self.xbegin = x
		self.ybegin = y
		self.xend = x+self.larg
		self.yend = y+self.haut

	"""the block position has the same position as the mouse"""
	def set_mouse_position(self, pos="center"):
		mx,  my = pygame.mouse.get_pos()
		if pos is "origin":
			self.set_position(mx, my)
		elif pos is "center":
			self.set_position(mx-self.larg//2, my-self.haut//2)
	"""the block move with a direction and a speed"""
	def move(self, direction, spd=None):
		speed = self.speed
		if spd is not None:
			speed = spd
		if direction == "right":
			self.xbegin += speed
		elif direction == "left":
			self.xbegin -= speed
		elif direction == "up":
			self.ybegin -= speed
		elif direction == "down":
			self.ybegin += speed
		self.set_position(self.xbegin, self.ybegin)

	"""the block is influenced by the gravity"""
	def gravity(self, g=10):
		self.speed = g*self.time
		self.ybegin += self.speed
		self.time = pygame.time.get_ticks()/1000
		self.set_position(self.xbegin, self.ybegin)

	"""delete the block from the classblock_list"""
	def delete_from_class_list(self):
		del Block.list_block[self.id]
		Block.nb_block -= 1

	"""detect a collision with a block (larg=1, haut=1)"""
	def cursor_collide(self, cursor):
		if cursor.xbegin >= self.xbegin and cursor.xbegin <= self.xend and cursor.ybegin >= self.ybegin and cursor.ybegin <= self.yend:
			return True
		return False

	"""detect a collision with a 1px/1px block and detect a keypress event"""
	def press_cursor_collide(self, cursor):
		if pygame.mouse.get_pressed()[0] and self.cursor_collide(cursor):
			return True
		return False

	"""activate a callback function"""
	def event(self, callback, args=None):
			if args == None:
				callback()
			else:
				callback(args)
	"""mult the size of the block by fact"""
	def mult_size(self, fact=1):
		if fact <= 0:
			return 'error'
		self.larg = int(self.larg * fact)
		self.haut = int(self.haut * fact)
		self.set_position(self.xbegin, self.ybegin)
	"""divide the size of the block by fact"""
	def div_size(self, fact=1):
		if fact <= 0:
			return 'error'
		self.larg = self.larg//fact
		self.haut = self.haut//fact
		self.set_position(self.xbegin, self.ybegin)
	"""pow the size of the block by fact"""
	def pow_size(self, power=2):
		if power < 0:
			return 'error'
		self.larg = self.larg**power
		self.haut = self.haut**power
		self.set_position(self.xbegin, self.ybegin)
	"""mult the size of the block by fact with *="""
	def __imul__(self, fact):
		if fact <= 0:
			return self
		self.larg = int(self.larg * fact)
		self.haut = int(self.haut * fact)
		self.set_position(self.xbegin, self.ybegin)
		return self
	"""divide the size of the block by fact with /="""
	def __itruediv__(self, fact):
		if fact <= 0:
			return self
		self.larg = self.larg//fact
		self.haut = self.haut//fact
		self.set_position(self.xbegin, self.ybegin)
		return self
	"""divide the size of the block by fact with //="""
	def __ifloordiv__(self, fact):
		if fact <= 0:
			return self
		self.larg = self.larg//fact
		self.haut = self.haut//fact
		self.set_position(self.xbegin, self.ybegin)
		return self
	"""pow the size of the block by fact with **="""
	def __ipow__(self, power):
		if power < 0:
			return self
		self.larg = self.larg**power
		self.haut = self.haut**power
		self.set_position(self.xbegin, self.ybegin)
		return self
	"""add the size of the block with an other block with <<"""
	def __lshift__(self, other):
		self.larg += other.larg
		self.haut += other.haut
		self.set_position(self.xbegin, self.ybegin)
	"""add the size of an other block with the instance with >>"""
	def __rshift__(self, other):
		other << self

	def __str__(self):
		return "{}x{} ({}x{}y)".format(self.larg, self.haut, self.xbegin, self.ybegin)

	def __repr__(self):
		string = "pos: ({}, {})\ndim: ({}, {})\nspeed: {}\nid: #{}\n".format(
			self.xbegin, self.ybegin, self.larg, self.haut, self.speed, self.id)
		return string




class Drawblock(Block):
	"""
	Drawblock -> visible drawing hitbox 
	color = the color of the block
	window = pygame.Surface()
	fill = 0-> the block is filled with color
	"""
	def __init__(self, x=0, y=0, larg=100, haut=100, speed=5, color=(255,255,255), fill=0, window=None):
		Block.__init__(self, x, y, larg, haut, speed)
		if window is None:
			print("Error: no window to draw block-id #{}".format(self.id))
			sys.exit(0)
		self.color = color
		self.window = window
		self.fill = fill
	"""draw the block on the screen"""
	def draw(self, form="rect"):
		if form is "rect":
			pygame.draw.rect(self.window, self.color, (self.xbegin, self.ybegin, self.larg, self.haut), self.fill)
		elif form is "circle":
			pygame.draw.circle(self.window, self.color, (int(self.xbegin), int(self.ybegin)), self.larg//2, self.fill)

	def __repr__(self):
		string = Block.__repr__(self)
		string += "color: {}".format(self.color)
		return string


class Picblock(Block):
	"""
	Picblock -> visible picture hitbox
	window = pygame.Surface()
	namepic = name of the picture
	pic = picture load
	"""
	def __init__(self, x=0, y=0, larg=100, haut=100, speed=0, namepic="unknown", window=None):
		Block.__init__(self, x, y, larg, haut, speed)
		if window is None:
			print("Error: no window to print block-id #{}".format(self.id))
			sys.exit(0)
		elif pic is "unknown":
			print("Error: impossible to load picture about block-id #{}".format(self.id))
			sys.exit(0)
		self.window = window
		self.namepic = namepic
		self.pic = pygame.image.load(self.namepic).convert_alpha()
		self.pic = pygame.transform.scale(self.pic, (self.larg, self.haut))
	"""print the picture block on the screen"""
	def print(self):
		self.window.blit(self.pic, (self.xbegin, self.ybegin))
	"""set the picture with an other pic and other dimensions"""
	def set_pic(self, pic, larg=None, haut=None):
		if larg is not None:
			self.larg = larg
		if haut is not None:
			self.haut = haut
		self.namepic = pic
		self.pic = pygame.image.load(self.namepic).convert_alpha()
		self.pic = pygame.transform.scale(self.pic, (self.larg, self.haut))
		self.set_position(self.xbegin, self.ybegin)

	def __repr__(self):
		string = Block.__repr__(self)
		string += "picture: {}".format(self.pic)
		return string





