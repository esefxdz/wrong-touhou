import pygame
import os
from constants import WIDTH, HEIGHT
import math
screen = pygame.display.set_mode((WIDTH, HEIGHT))

class spaceship:
    def __init__(self, x, y, map_w=3000, map_h=3000):
        super().__init__()
        self.map_w = map_w
        self.map_h = map_h
        self.rect = pygame.Rect(x, y, 50, 50)
        self.spaceship_image = pygame.image.load("textures/spaceship.png")
        self.spaceship_image = pygame.transform.scale(self.spaceship_image, (50, 50))
        self.spaceship_rect = self.spaceship_image.get_rect()
        self.spaceship_rect.center = (map_w // 2, map_h // 2)
        self.bullet_speed = 25
        self.bullets = []
        self.shoot_cooldown = 75
        self.last_shot_time = pygame.time.get_ticks()
        self.bullet_image = pygame.image.load("textures/bullet.png")
        self.bullet_image = pygame.transform.scale(self.bullet_image, (20, 40))
        
        self.max_hp = 5
        self.hit_count = 0
        self.enemies_killed = 0
        self.damage_dealt = 0
        
        from player_files.level import LevelSystem
        self.level_system = LevelSystem()

    def move(self, keys):
        keys = pygame.key.get_pressed()
        self.player_speed = 10
        if keys[pygame.K_a] and self.spaceship_rect.left > 0:
            self.spaceship_rect.x -= self.player_speed
        if keys[pygame.K_d] and self.spaceship_rect.right < self.map_w:
            self.spaceship_rect.x += self.player_speed
        if keys [pygame.K_w] and self.spaceship_rect.top > 0:
            self.spaceship_rect.y -= self.player_speed
        if keys[pygame.K_s] and self.spaceship_rect.bottom < self.map_h:
            self.spaceship_rect.y += self.player_speed

    def get_camera_offset(self):
        """Camera centers on player, clamped to map edges"""
        cam_x = self.spaceship_rect.centerx - WIDTH // 2
        cam_y = self.spaceship_rect.centery - HEIGHT // 2
        cam_x = max(0, min(cam_x, self.map_w - WIDTH))
        cam_y = max(0, min(cam_y, self.map_h - HEIGHT))
        return cam_x, cam_y

    def shoot(self, cam_offset):
        current_time = pygame.time.get_ticks()
        if pygame.key.get_pressed()[pygame.K_SPACE] and current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time

            # Get direction to mouse (mouse is in screen coords, convert to world)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_world_x = mouse_x + cam_offset[0]
            mouse_world_y = mouse_y + cam_offset[1]
            px, py = self.spaceship_rect.center
            dx = mouse_world_x - px
            dy = mouse_world_y - py
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 1

            direction = (dx / dist, dy / dist)
            self.bullets.append({
                "pos": [px, py],
                "dir": direction
            })

    def shoot_update(self, screen, cam_offset):
        new_bullets = []
        for bullet in self.bullets:
            bullet["pos"][0] += bullet["dir"][0] * self.bullet_speed
            bullet["pos"][1] += bullet["dir"][1] * self.bullet_speed

            screen_x = int(bullet["pos"][0]) - cam_offset[0]
            screen_y = int(bullet["pos"][1]) - cam_offset[1]
            bullet_rect = self.bullet_image.get_rect(center=(screen_x, screen_y))
            screen.blit(self.bullet_image, bullet_rect)

            if 0 <= bullet["pos"][0] <= self.map_w and 0 <= bullet["pos"][1] <= self.map_h:
                new_bullets.append(bullet)
        self.bullets = new_bullets


    def draw(self, screen, cam_offset):
        screen_x = self.spaceship_rect.x - cam_offset[0]
        screen_y = self.spaceship_rect.y - cam_offset[1]
        screen.blit(self.spaceship_image, (screen_x, screen_y))

    def take_hit(self):
        if self.hit_count < self.max_hp:
            self.hit_count += 1
            pygame.mixer.Sound(os.path.join("sounds", "hitsound.wav")).play()
            if self.hit_count >= self.max_hp:
                pass # death logic later
                
    def draw_health(self, screen):
        current_hp = self.max_hp - self.hit_count
        if current_hp < 0:
            current_hp = 0

        bar_width = 300
        bar_height = 20
        x_pos = (WIDTH // 2) - (bar_width // 2)
        y_pos = 20
        
        fill_width = (current_hp / self.max_hp) * bar_width

        pygame.draw.rect(screen, (255, 0, 0), (x_pos, y_pos, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (x_pos, y_pos, fill_width, bar_height))
        
        font = pygame.font.Font(None, 30)
        hp_text = font.render(f"{current_hp} / {self.max_hp}", True, (255, 255, 255))
        text_rect = hp_text.get_rect(center=(WIDTH // 2, y_pos + bar_height // 2))
        screen.blit(hp_text, text_rect)