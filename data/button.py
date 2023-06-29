import pygame 

#button class
class Button():
	def __init__(self,x, y, image, scale):
		self.scale = scale
		self.image = image
		self.image.set_alpha(0)
		self.rect = self.image.get_rect()
		self.rect.width = self.image.get_width()
		self.rect.height = self.image.get_height()
		self.rect.topleft = (x/self.scale, y/self.scale)
		self.clicked = False
		self.color = (255, 255, 0)

	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()
		posx = pos[0]/self.scale
		posy = pos[1]/self.scale

		#check mouseover and clicked conditions
		if self.rect.collidepoint((posx, posy)):
			self.color = (255, 0, 0)
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True
		else:
			self.color = (255, 255, 0)

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, self.rect)

		return action