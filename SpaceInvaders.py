import pygame
import os
import time 
import random
pygame.font.init()



WIDTH,HEIGHT=720,720   #Window Size
WIN=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Invader")

#LOADING ASSETS / IMAGES :
RED_SPACE_SHIP=pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))  #Enemy Ship1
GREEN_SPACE_SHIP=pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))  #Enemy Ship2
BLUE_SPACE_SHIP=pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))   #Enemy Ship3
YELLOW_SPACE_SHIP=pygame.image.load(os.path.join("assets","pixel_ship_yellow.png"))   #Player Ship
RED_LASER=pygame.image.load(os.path.join("assets","pixel_laser_red.png"))  #Red Laser
GREEN_LASER=pygame.image.load(os.path.join("assets","pixel_laser_green.png"))  #Green Laser
BLUE_LASER=pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))  #Blue Laser
YELLOW_LASER=pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))  #Yellow Laser
BG=pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")),(WIDTH,HEIGHT))  #Background Image

#Laser Class
class Laser:
	def __init__(self,x,y,img):
		self.x=x
		self.y=y
		self.img=img
		self.mask =pygame.mask.from_surface(self.img)

	def draw(self,window):
		window.blit(self.img,(self.x,self.y))

	def move(self,vel):
		self.y += vel

	def off_screen(self,height):
		return not (self.y <= height and self.y>=0)

	def collision(self,obj):
		return collide(obj,self)

#General Ship Class
class Ship:
	COOLDOWN=30
	def __init__(self,x,y,health=100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img=None
		self.laser_img=None
		self.lasers=[]
		self.cool_down_counter=0

	def draw(self,window):
		window.blit(self.ship_img,(self.x,self.y))
		for laser in self.lasers:
			laser.draw(window)

	def move_lasers(self,vel,obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health-=10
				self.lasers.remove(laser)

	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter =0
		elif self.cool_down_counter >0:
			self.cool_down_counter +=1

	def shoot(self):
		if self.cool_down_counter == 0:
			laser=Laser(self.x,self.y,self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter =1

	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height()


#Player Ship class with inherited features from Ship Class
class Player(Ship):
	def __init__(self,x,y,health=100):
		super().__init__(x,y,health) #using initialisation from top
		self.ship_img =YELLOW_SPACE_SHIP
		self.laser_img=YELLOW_LASER
		self.mask =pygame.mask.from_surface(self.ship_img)
		self.max_health=health

	def move_lasers(self,vel,objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						self.lasers.remove(laser)

	def draw(self,window):
		super().draw(window)
		self.healthbar(window)

	def healthbar(self,window):
		pygame.draw.rect(window,(255,0,0),(self.x,self.y+self.ship_img.get_height()+10,self.ship_img.get_width(),10))
		pygame.draw.rect(window,(0,255,0),(self.x,self.y+self.ship_img.get_height()+10,self.ship_img.get_width()*(self.health/self.max_health),10))

#Enemy Ship class with inherited features from Ship Class
class Enemy(Ship):
	COLOR_MAP=  {	
				"red":(RED_SPACE_SHIP,RED_LASER),
				"green":(GREEN_SPACE_SHIP,GREEN_LASER),
				"blue":(BLUE_SPACE_SHIP,BLUE_LASER)
				}

	def __init__(self,x,y,color,health=100):
		super().__init__(x,y,health)
		self.ship_img,self.laser_img =self.COLOR_MAP[color]
		self.mask =pygame.mask.from_surface(self.ship_img)

	def move(self,vel):
		self.y+=vel

	def shoot(self):
		if self.cool_down_counter == 0:
			laser=Laser(self.x-15,self.y,self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter =1


#Collide function to check if laser has collided with Ship
def collide(obj1,obj2):
	offset_x =obj2.x - obj1.x
	offset_y =obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask,(offset_x, offset_y)) != None 

#Main function to put everything together in one whole piece
def main():
	run=True
	FPS=60  
	level=0
	lives=5
	main_font=pygame.font.SysFont("comicsans",30)
	lost_font=pygame.font.SysFont("comicsans",70)
	player_vel=5
	lost=False
	lost_count=0
	laser_vel = 6
	enemies= []  #Stores enemy location
	wave_length = 5
	enemy_vel=1
	player=Player(300,600)
	clock=pygame.time.Clock()

	def redraw_window():
		WIN.blit(BG,(0,0))   #(0,0) is top left . downwards increase y and increase x to move rightward
	 	
		lives_label = main_font.render(f"Lives:{lives}",1,(255,255,255))
		level_label = main_font.render(f"Level:{level}",1,(255,255,255))

		WIN.blit(lives_label,(10,10))
		WIN.blit(level_label,(WIDTH - level_label.get_width()-10,10))


		for enemy in enemies:
			enemy.draw(WIN)

		player.draw(WIN)

		if lost:
			lost_label=lost_font.render("GAME OVER",1,(255,0,0))
			WIN.blit(lost_label,(WIDTH/2-lost_label.get_width()/2,350))

		pygame.display.update()                   #refreshes the window (redraws everything 60FPS)

	while run:
		clock.tick(FPS)		
		redraw_window()

		if lives <=0 or player.health <=0:
			lost=True
			lost_count+=1

		if lost:
			if lost_count > FPS*3:
				run=False
			else:
				continue

		if len(enemies)==0:
			level+=1
			wave_length+=5 
			for i in range(wave_length):
				enemy = Enemy(random.randrange(50, WIDTH-100),random.randrange(-1500,-100),random.choice(['red','blue','green']))
				enemies.append(enemy)
		
		for event in pygame.event.get():
			if event.type== pygame.QUIT:
				quit()

		keys=pygame.key.get_pressed()
		if keys[pygame.K_a] and player.x-player_vel >0:
			player.x -= player_vel
		if keys[pygame.K_d] and player.x+player_vel +player.get_width() <WIDTH :
			player.x += player_vel
		if keys[pygame.K_w] and player.y-player_vel >0:
			player.y -= player_vel
		if keys[pygame.K_s] and player.y+player_vel +player.get_height()+15 <HEIGHT:
			player.y += player_vel
		if keys[pygame.K_SPACE]:
			player.shoot()

		for enemy in enemies[:]:
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel, player)

			if random.randrange(0, 2*60)==1:
				enemy.shoot()

			if collide(enemy,player):
				player.health-=10
				enemies.remove(enemy)
			elif enemy.y +enemy.get_height()>HEIGHT:
				lives -=1
				enemies.remove(enemy)

			if collide(enemy,player):
				player.health-=10
				enemies.remove(enemy)

		player.move_lasers(-laser_vel,enemies)

# Function to create Main menu
def main_menu():
	title_font=pygame.font.SysFont("comicsans",70)
	run=True
	while run:
		WIN.blit(BG,(0,0))
		title_label=title_font.render("Press mouse to begin",1,(255,255,255))
		WIN.blit(title_label,(WIDTH/2 - title_label.get_width()/2,350))
		pygame.display.update()


		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				run=False
			if event.type==pygame.MOUSEBUTTONDOWN:
				main()
	pygame.quit()


if __name__=='__main__':
    main_menu()



