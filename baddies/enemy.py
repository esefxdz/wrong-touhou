import sys
import os
import wave
import pygame
pygame.mixer.init()

#doesnt work
sys.path.append(
    os.path.dirname(os.path.dirname(__file__))
) 
import constants # is this the way we import constants then its stupid lmao

class rumia:
    def __init__(self):
        super().__init__()

        pygame.mixer.init()
        kill_sound_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "killsound.wav")
        self.kill_sound = kill_sound_path

        self.lolrect = pygame.Rect(100, 100, 50, 50)
        self.image_path = os.path.join(os.path.dirname(__file__), "rumia.png")
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rumia_rect = self.image.get_rect()

        #health
        self.max_hp = 10
        self.hit_count = 0
        self.defeated = False

        #move
        self.speed = 5
        self.direction = 1
        self.screen_width = constants.WIDTH

        # move
        self.speed = 5
        self.direction = 1
        self.screen_width = constants.WIDTH

        # shooty shoot
        self.last_fire_time = pygame.time.get_ticks()
        self.fire_cooldown = 1000
        self.fires = []
        self.fire_speed = 10

    # THIS AREA IS WEIRD!!!!!!!!!!!!!
    def fire(self):
        current_time = pygame.time.get_ticks()
        if self.defeated == False:
            if current_time - self.last_fire_time >= self.fire_cooldown:
                fire_rect = pygame.Rect(self.lolrect.centerx - 5, self.lolrect.bottom, 10, 20)
                self.fires.append(fire_rect)
                self.last_fire_time = current_time
        if self.defeated == True:
            return

    def update_fire(self, screen):
        for fire in self.fires[:]:
            fire.y += self.fire_speed
            pygame.draw.rect(screen, constants.RED, fire)
            if fire.top > 1000:
                self.fires.remove(fire)

    # END OF WEIRD AREA!!!!!!!!!!!!!!!

    def take_hit(self):
        if not self.defeated:
            self.hit_count += 1
            print(f"Rumia hit {self.hit_count}")
            pygame.mixer.Sound(os.path.join("sounds", "hitsound.wav")).play()
            if self.hit_count >= self.max_hp:
                self.defeated = True
                pygame.mixer.Sound(os.path.join("sounds", "killsound.wav")).play()
                ############


    def move(self, WIDTH):
        self.lolrect.x += self.speed * self.direction
        if self.lolrect.right >= WIDTH or self.lolrect.left <= 0:
            self.direction *= -1

    def draw(self, screen):
        if not self.defeated:
            screen.blit(self.image, self.lolrect)
