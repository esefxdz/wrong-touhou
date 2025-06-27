import sys
import os
import wave
import pygame
import random
import math
pygame.mixer.init()

# Append the root directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import constants

class rumia:
    def __init__(self, player_ref):
        super().__init__()
        self.player = player_ref

        kill_sound_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "killsound.wav")
        self.kill_sound = kill_sound_path

        self.image_path = os.path.join(os.path.dirname(__file__), "rumia.png")
        self.image = pygame.image.load(self.image_path)
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rumia_rect = self.image.get_rect()

        self.spawn_outside_screen()

        # health
        self.max_hp = 2
        self.hit_count = 0
        self.defeated = False

        # move toward player
        self.speed = 0.5 # lower than 5 for more natural chase
        self.screen_width = constants.WIDTH

        # shoot
        self.last_fire_time = pygame.time.get_ticks()
        self.fire_cooldown = 1000
        self.fires = []
        self.fire_speed = 10

    def spawn_outside_screen(self):
        screen_w, screen_h = constants.WIDTH, constants.HEIGHT
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, screen_w)
            y = -self.rumia_rect.height
        elif side == 'bottom':
            x = random.randint(0, screen_w)
            y = screen_h
        elif side == 'left':
            x = -self.rumia_rect.width
            y = random.randint(0, screen_h)
        else:  # right
            x = screen_w
            y = random.randint(0, screen_h)
        self.rumia_rect.topleft = (x, y)
        self.lolrect = pygame.Rect(x, y, 50, 50)  # still used for fire origin

    def fire(self):
        if self.defeated:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire_time > self.fire_cooldown:
            self.last_fire_time = current_time

            # Fire toward player
            enemy_x, enemy_y = self.lolrect.center
            player_x, player_y = self.player.spaceship_rect.center

            dx = player_x - enemy_x
            dy = player_y - enemy_y
            distance = math.hypot(dx, dy)
            if distance == 0:
                distance = 1

            direction = (dx / distance, dy / distance)

            self.fires.append({
                "pos": [enemy_x, enemy_y],
                "dir": direction
            })

    def update_fire(self, screen):
        if self.defeated:
            return
        for fire in self.fires:
            fire["pos"][0] += fire["dir"][0] * 3  # move horizontally
            fire["pos"][1] += fire["dir"][1] * 3  # move vertically

    def take_hit(self):
        if not self.defeated:
            self.hit_count += 1
            pygame.mixer.Sound(os.path.join("sounds", "hitsound.wav")).play()
            if self.hit_count >= self.max_hp:
                self.defeated = True
                self.fires.clear()
                pygame.mixer.Sound(os.path.join("sounds", "killsound.wav")).play()

    def move_toward_player(self):
        enemy_x = self.lolrect.centerx
        enemy_y = self.lolrect.centery
        player_x = self.player.spaceship_rect.centerx
        player_y = self.player.spaceship_rect.centery

        dx = player_x - enemy_x
        dy = player_y - enemy_y

        distance = math.hypot(dx, dy)
        if distance == 0:
            return  # Already at the player

        dx = dx / distance
        dy = dy / distance

        speed = 1.5
        self.lolrect.x += dx * speed
        self.lolrect.y += dy * speed

    def update(self, screen):
        if self.defeated:
            return  # Stop all behavior if defeated
        self.move_toward_player()
        self.update_fire(screen)


    def draw(self, screen):
        if not self.defeated:
            screen.blit(self.image, self.lolrect)
        for fire in self.fires:
            pygame.draw.circle(screen, (255, 0, 0), (int(fire["pos"][0]), int(fire["pos"][1])), 5)

