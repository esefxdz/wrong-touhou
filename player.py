import pygame
from constants import WIDTH, HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
keys_pressed = pygame.key.get_pressed

class spaceship:
    def __init__(self, screen):
        super().__init__()
        self.spaceship_image = pygame.image.load("spaceship.png")
        self.spaceship_image = pygame.transform.scale(self.spaceship_image, (50, 50))
        self.spaceship_rect = self.spaceship_image.get_rect()
        self.spaceship_rect.center = (WIDTH // 2, HEIGHT // 2)
        self.bullet_speed = 25
        self.bullets = []
        self.shoot_cooldown = 75
        self.last_shot_time = pygame.time.get_ticks()
        self.bullet_image = pygame.image.load("bullet.png")
        self.bullet_image = pygame.transform.scale(self.bullet_image, (20, 40))

    def move(self, keys):
        keys = pygame.key.get_pressed()
        self.player_speed = 10
        if keys[pygame.K_LEFT] and self.spaceship_rect.left > 0:
            self.spaceship_rect.x -= self.player_speed
        if keys[pygame.K_RIGHT] and self.spaceship_rect.right < WIDTH:
            self.spaceship_rect.x += self.player_speed
        if keys [pygame.K_UP] and self.spaceship_rect.top > 0:
            self.spaceship_rect.y -= self.player_speed
        if keys[pygame.K_DOWN] and self.spaceship_rect.bottom < HEIGHT:
            self.spaceship_rect.y += self.player_speed

    def shoot(self):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        #cooldown confirmer
        if keys[pygame.K_SPACE] and current_time - self.last_shot_time >= self.shoot_cooldown:
            bullet_rect = pygame.Rect(self.spaceship_rect.centerx - 5, self.spaceship_rect.top, 10, 20)
            self.bullets.append(bullet_rect)
            #cooldown resetter
            self.last_shot_time = current_time

    def shoot_update(self, screen):
        for bullet in self.bullets:
            bullet.y -= self.bullet_speed
            screen.blit(self.bullet_image, bullet)
            if bullet.bottom < 0:
                self.bullets.remove(bullet)

    def draw(self, screen):
        screen.blit(self.spaceship_image, self.spaceship_rect)