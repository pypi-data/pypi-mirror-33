from izipygame import *
#TEST FILE
pygame.font.init()
fenetre = Window(1200, 800, "os")
p = Policestr(name=None, size=40, string="text", color=(250,0,0), window=fenetre.get_canva(), x=0, y=0)
b = Drawblock(window=fenetre.get_canva(), y=200, x=300)
a = Drawblock(window=fenetre.get_canva(), y=200, x=300)
print(str(p))
pygame.init()



fini = False
temps = pygame.time.Clock()
while not fini:
	mx,  my = pygame.mouse.get_pos()
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			fini = True
		if event.type == KEYUP:
			if event.key == K_q:
				fini = True
			if event.key == K_a:
				p += 2



	temps.tick(60)
	fenetre.fill((0,255,20))
	p.write()
	b.draw()



	pygame.display.flip()
pygame.quit()


