import sys
import os
import pygame
sys.path.append(os.path.dirname(__file__)) #is this the way we import constants then its stupid lmao
import constants  # noqa: F401

class rumia:
    def __init__(self):
        super().__init__()
        self.lolrect = pygame.Rect(100, 100, 50, 50)
        self.image_path = os.path.join(os.path.dirname(__file__), "rumia.png")
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rumia_rect = self.image.get_rect()

        #moveshe 
        self.speed = 5
        self.direction = 1
        self.screen_width = constants.WIDTH

        #shooty shoot
        self.last_fire_time = pygame.time.get_ticks()
        self.fire_cooldown = 1000
        self.fires = []
        self.fire_speed = 10

    # THIS AREA IS WEIRD!!!!!!!!!!!!!
    def fire(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire_time >= self.fire_cooldown:
            fire_rect = pygame.Rect(self.lolrect.centerx - 5, self.lolrect.bottom, 10, 20)
            self.fires.append(fire_rect)
            self.last_fire_time = current_time

    def update_fire(self, screen):
        for fire in self.fires[:]:
            fire.y += self.fire_speed
            pygame.draw.rect(screen, constants.RED, fire)
            if fire.top > 1000:
                self.fires.remove(fire)
    # END OF WEIRD AREA!!!!!!!!!!!!!!!

    def move(self, WIDTH):
        self.lolrect.x += self.speed * self.direction
        if self.lolrect.right >= WIDTH or self.lolrect.left <= 0:
            self.direction *= -1

    def draw(self, screen):
        screen.blit(self.image, self.lolrect)
