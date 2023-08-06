import pygame, pygame.mixer
from pygame.locals import*
import sys


class Window:
	"""
	Window -> create a basic pygame window
	win: the pygame window -> pygame.Surface()
	wlarg = width of the window
	whaut = height of the window
	wtitle = title of the window
	"""
	def __init__(self, wlarg=500, whaut=500, wtitle="unknown"):
		self.wlarg = wlarg
		self.whaut = whaut
		self.wtitle = wtitle
		self.win = pygame.display.set_mode((wlarg, whaut))
		pygame.display.set_caption(wtitle)

	"""same role as Surface.fill()"""
	def fill(self, color):
		self.win.fill(color)
	"""return the pygame window"""
	def get_canva(self):
		return self.win
	"""set the size of the window"""
	def set_size(self, wlarg=500, whaut=500):
		self.wlarg = wlarg
		self.whaut = whaut
		self.win = pygame.display.set_mode((wlarg, whaut))
	"""set the title of the window"""
	def set_title(self, string):
		pygame.display.set_caption(string)
