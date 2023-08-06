import pygame, pygame.mixer
from pygame.locals import*
import sys


class Window:
	"""
	Window -> create a basic pygame window
	win: the pygame window -> pygame.Surface()
	wwidth = width of the window
	wheight = height of the window
	wtitle = title of the window
	"""
	def __init__(self, wwidth=500, wheight=500, wtitle="unknown"):
		self.wwidth = wwidth
		self.wheight = wheight
		self.wtitle = wtitle
		self.win = pygame.display.set_mode((wwidth, wheight))
		pygame.display.set_caption(wtitle)

	"""same role as Surface.fill()"""
	def fill(self, color):
		self.win.fill(color)
	"""return the pygame window"""
	def get_canva(self):
		return self.win
	"""set the size of the window"""
	def set_size(self, wwidth=500, wheight=500):
		self.wwidth = wwidth
		self.wheight = wheight
		self.win = pygame.display.set_mode((wwidth, wheight))
	"""set the title of the window"""
	def set_title(self, string):
		pygame.display.set_caption(string)
