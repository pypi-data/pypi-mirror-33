from izi_pygame.izipygame import *
import os
name = "izi_pygame"
file = __file__.split('/')
file[len(file)-1] = "doc/index.html"
j = 0
string = str()
for i in file:
	file[j] += '/'
	string += file[j]
	j+=1
doc_travel = string[0:len(string)-1]
doc = lambda:os.system("open {}".format(doc_travel))