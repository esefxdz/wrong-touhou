import pygame
from constants import WIDTH, HEIGHT
from baddies.enemy import rumia
import math
screen = pygame.display.set_mode((WIDTH, HEIGHT))
keys_pressed = pygame.key.get_pressed
enemy = rumia

class spaceship:
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 50, 50)
        self.spaceship_image = pygame.image.load("textures/spaceship.png")
        self.spaceship_image = pygame.transform.scale(self.spaceship_image, (50, 50))
        self.spaceship_rect = self.spaceship_image.get_rect()
        self.spaceship_rect.center = (WIDTH // 2, HEIGHT // 2)
        self.bullet_speed = 25
        self.bullets = []
        self.shoot_cooldown = 75
        self.last_shot_time = pygame.time.get_ticks()
        self.bullet_image = pygame.image.load("textures/bullet.png")
        self.bullet_image = pygame.transform.scale(self.bullet_image, (20, 40))

    def move(self, keys):
        keys = pygame.key.get_pressed()
        self.player_speed = 10
        if keys[pygame.K_a] and self.spaceship_rect.left > 0:
            self.spaceship_rect.x -= self.player_speed
        if keys[pygame.K_d] and self.spaceship_rect.right < WIDTH:
            self.spaceship_rect.x += self.player_speed
        if keys [pygame.K_w] and self.spaceship_rect.top > 0:
            self.spaceship_rect.y -= self.player_speed
        if keys[pygame.K_s] and self.spaceship_rect.bottom < HEIGHT:
            self.spaceship_rect.y += self.player_speed

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if pygame.key.get_pressed()[pygame.K_SPACE] and current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time

            # Get direction to mouse
            mouse_x, mouse_y = pygame.mouse.get_pos()
            px, py = self.spaceship_rect.center
            dx = mouse_x - px
            dy = mouse_y - py
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 1

            direction = (dx / dist, dy / dist)
            self.bullets.append({
                "pos": [px, py],
                "dir": direction
            })

    def shoot_update(self, screen):
        new_bullets = []
        for bullet in self.bullets:
            bullet["pos"][0] += bullet["dir"][0] * self.bullet_speed
            bullet["pos"][1] += bullet["dir"][1] * self.bullet_speed

            bullet_rect = self.bullet_image.get_rect(center=(int(bullet["pos"][0]), int(bullet["pos"][1])))
            screen.blit(self.bullet_image, bullet_rect)

            if 0 <= bullet["pos"][0] <= WIDTH and 0 <= bullet["pos"][1] <= HEIGHT:
                new_bullets.append(bullet)
        self.bullets = new_bullets


    def draw(self, screen):
        screen.blit(self.spaceship_image, self.spaceship_rect)