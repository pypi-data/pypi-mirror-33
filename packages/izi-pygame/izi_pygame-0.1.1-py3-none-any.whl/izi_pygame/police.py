import pygame, pygame.mixer
from pygame.locals import*
import sys
#police = font
class Policestr:
	"""
	Policestr -> create a drawing string and the police
	police = pygame.font.Font()
	policename = the name of the police
	policesize = the size of the police
	txt = text to assign the police
	string = texte to print
	color = color of the string
	window = pygame.Surface()
	x and y = posiiton of the text
	"""
	def __init__(self, name=None, size=20, string="text", color=(0,0,0), window=None, x=0, y=0, italic=0, bold=0, underline=0):
		self.police = pygame.font.Font(name, size)
		self.police.set_italic(italic)
		self.police.set_bold(bold)
		self.police.set_underline(underline)
		self.policename = name
		self.policesize = size
		self.txt = string
		self.string = self.police.render(string, True, color)
		self.color = color
		if window is None:
			print("police error: no window")
			sys.exit(0)
		self.window = window
		self.x = x
		self.y = y
	"""update the printed string"""
	def refresh(self):
		self.string = self.police.render(self.txt, True, self.color)
	"""print the string"""
	def write(self):
		self.window.blit(self.string, (self.x, self.y))
	"""set the text to print"""
	def set_text(self, string):
		if type(string) is not str:
			string = str(string)
		self.txt = string
		self.refresh()
	"""return the text printed"""
	def get_text(self):
		return self.txt
	"""set the policename and his size"""
	def set_font(self, name=None, size=None):
		if name is not None:
			self.policename = name
		if size is not None:
			self.policesize = size
		self.police = pygame.font.Font(self.policename, self.policesize)
		self.refresh()
	"""set the style of the police"""
	def set_style(self, it=False, bd=False, ul=False):
		self.police.set_italic(it)
		self.police.set_bold(bd)
		self.police.set_underline(ul)
		self.refresh()

	"""set the text of the string with <<"""
	def __lshift__(self, string):
		if type(string) is not str:
			string = str(string)
		self.txt = string
		self.refresh()
	"""up the policesize with +="""
	def __iadd__(self, fact):
		if fact < 0:
			return self
		self.set_font(size=int(self.policesize+fact))
		self.refresh()
		return self
	"""down the policesize with -="""
	def __isub__(self, fact):
		if fact < 0:
			return self
		self.set_font(size=int(self.policesize-fact))
		self.refresh()
		return self
	"""mult the policesize with *="""
	def __imul__(self, fact):
		if fact < 0:
			return self
		self.set_font(size=int(self.policesize*fact))
		self.refresh()
		return self
	"""divide the policesize with /="""
	def __itruediv__(self, fact):
		if fact < 0:
			return self
		self.set_font(size=int(self.policesize//fact))
		self.refresh()
		return self
	"""divide the policesize with //="""
	def __ifloordiv__(self, fact):
		if fact < 0:
			return self
		self.set_font(size=int(self.policesize//fact))
		self.refresh()
		return self
	"""return the text of the string with str(self)"""
	def __str__(self):
		return self.get_text()

	def __repr__(self):
		return "font: {}\nsize: {}\ntext: {}\ncolor: {}\nitalic: {}\nbold: {}\nunderline: {}".format(
			self.policename, self.policesize, self.txt, self.color,
			self.police.get_italic(), self.police.get_bold(), self.police.get_underline()
			)



