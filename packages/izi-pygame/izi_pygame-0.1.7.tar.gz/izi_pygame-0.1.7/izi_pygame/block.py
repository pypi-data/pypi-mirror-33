import pygame, pygame.mixer
from pygame.locals import*
import sys

class Block:
	"""
	Block -> hitbox no visible
	xbegin = xorigin of the block
	ybegin = yorigin of the block
	width = width of the block
	height = height of the block
	speed = the speed of the block if it moved
	id = the id of the block
	"""
	nb_block = 0
	list_block = []
	def __init__(self, x=0, y=0, width=100, height=100, speed=5):
		self.xbegin = x
		self.ybegin = y
		self.width = width
		self.height = height
		self.rect = pygame.Rect(x, y, width, height)
		self.xend = x+width
		self.yend = y+height
		self.speed = speed
		self.id = Block.nb_block
		self.time = None
		Block.nb_block += 1
		Block.list_block.append(self)
	"""set the position of the block"""
	def set_position(self, x, y):
		self.xbegin = x
		self.ybegin = y
		self.xend = x+self.width
		self.yend = y+self.height
		self.rect = pygame.Rect(x, y, self.width, self.height)
	"""set the dimanension of the block"""
	def set_dimension(self, width=None, height=None):
		new_width = width
		new_height = height
		if width is None:
			new_width = self.width
		if height is None:
			new_height = self.height
		self.width = new_width
		self.height = new_height
		self.set_position(self.xbegin, self.ybegin)
	"""detect collision between rects"""
	def is_in_collision_with(self, other):
		if type(other) is list:
			return self.rect.collidelist(other)
		else:
			return self.rect.colliderect(other)
	#alias
	collision = is_in_collision_with

	"""the block position has the same position as the mouse"""
	def set_mouse_position(self, pos="center"):
		mx,  my = pygame.mouse.get_pos()
		if pos is "origin":
			self.set_position(mx, my)
		elif pos is "center":
			self.set_position(mx-self.width//2, my-self.height//2)
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

	"""detect a collision with a block (width=1, height=1)"""
	def cursor_collide(self, cursor):
		if cursor.xbegin >= self.xbegin and cursor.xbegin <= self.xend and cursor.ybegin >= self.ybegin and cursor.ybegin <= self.yend:
			return True
		return False

	"""detect a collision with a 1px/1px block and detect a keypress event"""
	def press_cursor_collide(self, cursor):
		if pygame.mouse.get_pressed()[0] and self.cursor_collide(cursor):
			return True
		return False

	"""mult the size of the block by fact"""
	def mult_size(self, fact=1):
		if fact <= 0:
			return 'error'
		self.width = int(self.width * fact)
		self.height = int(self.height * fact)
		self.set_position(self.xbegin, self.ybegin)
	"""divide the size of the block by fact"""
	def div_size(self, fact=1):
		if fact <= 0:
			return 'error'
		self.width = self.width//fact
		self.height = self.height//fact
		self.set_position(self.xbegin, self.ybegin)
	"""pow the size of the block by fact"""
	def pow_size(self, power=2):
		if power < 0:
			return 'error'
		self.width = self.width**power
		self.height = self.height**power
		self.set_position(self.xbegin, self.ybegin)
	"""mult the size of the block by fact with *="""
	def __imul__(self, fact):
		if fact <= 0:
			return self
		self.width = int(self.width * fact)
		self.height = int(self.height * fact)
		self.set_position(self.xbegin, self.ybegin)
		return self
	"""divide the size of the block by fact with /="""
	def __itruediv__(self, fact):
		if fact <= 0:
			return self
		self.width = self.width//fact
		self.height = self.height//fact
		self.set_position(self.xbegin, self.ybegin)
		return self
	"""divide the size of the block by fact with //="""
	def __ifloordiv__(self, fact):
		if fact <= 0:
			return self
		self.width = self.width//fact
		self.height = self.height//fact
		self.set_position(self.xbegin, self.ybegin)
		return self
	"""pow the size of the block by fact with **="""
	def __ipow__(self, power):
		if power < 0:
			return self
		self.width = self.width**power
		self.height = self.height**power
		self.set_position(self.xbegin, self.ybegin)
		return self
	"""add the size of the block with an other block with <<"""
	def __lshift__(self, other):
		self.width += other.width
		self.height += other.height
		self.set_position(self.xbegin, self.ybegin)
	"""add the size of an other block with the instance with >>"""
	def __rshift__(self, other):
		other << self

	def __str__(self):
		return "{}x{} ({}x{}y)".format(self.width, self.height, self.xbegin, self.ybegin)

	def __repr__(self):
		string = "pos: ({}, {})\ndim: ({}, {})\nspeed: {}\nid: #{}\n".format(
			self.xbegin, self.ybegin, self.width, self.height, self.speed, self.id)
		return string




class Drawblock(Block):
	"""
	Drawblock -> visible drawing hitbox 
	color = the color of the block
	window = pygame.Surface()
	fill = 0-> the block is filled with color
	"""
	def __init__(self, x=0, y=0, width=100, height=100, speed=5, color=(255,255,255), fill=0, window=None):
		Block.__init__(self, x, y, width, height, speed)
		if window is None:
			print("Error: no window to draw block-id #{}".format(self.id))
			sys.exit(0)
		self.color = color
		self.window = window
		self.fill = fill
	"""draw the block on the screen"""
	def draw(self, form="rect"):
		if form is "rect":
			pygame.draw.rect(self.window, self.color, self.rect, self.fill)
		elif form is "circle":
			pygame.draw.circle(self.window, self.color, (int(self.xbegin), int(self.ybegin)), self.width//2, self.fill)

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
	def __init__(self, x=0, y=0, width=100, height=100, speed=0, namepic=None, window=None):
		Block.__init__(self, x, y, width, height, speed)
		if window is None:
			print("Error: no window to print block-id #{}".format(self.id))
			sys.exit(0)
		elif namepic is None:
			print("Error: impossible to load picture about block-id #{}".format(self.id))
			sys.exit(0)
		self.window = window
		self.namepic = namepic
		self.pic = pygame.image.load(self.namepic).convert_alpha()
		self.pic = pygame.transform.scale(self.pic, (self.width, self.height))
	"""print the picture block on the screen"""
	def print(self):
		self.window.blit(self.pic, (self.xbegin, self.ybegin))
	def set_dimension(self, width=None, height=None):
		new_width = width
		new_height = height
		if width is None:
			new_width = self.width
		if height is None:
			new_height = self.height
		self.width = new_width
		self.height = new_height
		self.rect = pygame.Rect(self.xbegin, self.ybegin, new_width, new_height)
		self.pic = pygame.transform.scale(self.pic, (self.width, self.height))
		self.set_position(self.xbegin, self.ybegin)
	"""set the picture with an other pic and other dimensions"""
	def set_pic(self, pic, width=None, height=None):
		if width is not None:
			self.width = width
		if height is not None:
			self.height = height
		self.namepic = pic
		self.pic = pygame.image.load(self.namepic).convert_alpha()
		self.pic = pygame.transform.scale(self.pic, (self.width, self.height))
		self.set_position(self.xbegin, self.ybegin)

	def __repr__(self):
		string = Block.__repr__(self)
		string += "picture: {}".format(self.pic)
		return string





