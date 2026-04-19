import pygame
import os
from constants import WIDTH, HEIGHT, ORANGE, WHITE, RED, GREEN, FONT_SMALL
import math
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
        self.shoot_cooldown = 75
        self.last_shot_time = pygame.time.get_ticks()
        self.max_hp = 5
        self.hit_count = 0
        self.enemies_killed = 0
        self.damage_dealt = 0

        # Touhou-style hitbox circles (world-space radii)
        self.hitbox_radius = 6    # tiny core — actual damage circle
        self.graze_radius  = 28   # larger invisible ring — bullets passing through grant XP

        # Graze state: set of bullet indices already counted this logical frame
        self.grazed_this_frame: set = set()

        # Damage flash visual
        self._hit_flash_until = 0
        
        # Dash and iframe variables
        self.is_dashing = False
        self.dash_cooldown = 1000
        self.last_dash_time = 0
        self.dash_duration = 200
        self.dash_speed_multiplier = 3.5
        self.dash_dir = (0, 0)
        self.invincible_until = 0
        self.afterimages = []
        
        from player_files.level import LevelSystem
        self.level_system = LevelSystem()

    def move(self, keys):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        self.player_speed = 10

        if self.is_dashing:
            if current_time - self.last_dash_time > self.dash_duration:
                self.is_dashing = False
            else:
                self.spaceship_rect.x += self.dash_dir[0] * self.player_speed * self.dash_speed_multiplier
                self.spaceship_rect.y += self.dash_dir[1] * self.player_speed * self.dash_speed_multiplier
                
                # Clamp to map boundaries
                self.spaceship_rect.x = max(0, min(self.spaceship_rect.x, self.map_w - self.spaceship_rect.width))
                self.spaceship_rect.y = max(0, min(self.spaceship_rect.y, self.map_h - self.spaceship_rect.height))
                
                if len(self.afterimages) == 0 or current_time - self.afterimages[-1][3] > 40:
                    self.afterimages.append((self.spaceship_image.copy(), self.spaceship_rect.x, self.spaceship_rect.y, current_time))
                return

        if keys[pygame.K_LSHIFT] and current_time - self.last_dash_time > self.dash_cooldown:
            dx, dy = 0, 0
            if keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_d]: dx += 1
            if keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_s]: dy += 1
            
            if dx != 0 or dy != 0:
                dist = math.hypot(dx, dy)
                self.dash_dir = (dx/dist, dy/dist)
                self.is_dashing = True
                self.last_dash_time = current_time
                self.invincible_until = current_time + self.dash_duration
                self.afterimages.append((self.spaceship_image.copy(), self.spaceship_rect.x, self.spaceship_rect.y, current_time))
                return

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

    def shoot(self, cam_offset, proj_manager):
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
            # owner=0 means player bullet
            angle = math.atan2(direction[1], direction[0])
            proj_manager.spawn(
                px, py, direction[0], direction[1], self.bullet_speed,
                radius=10, color=WHITE, type_id=1, owner=0, angle=angle
            )

    def draw(self, screen, cam_offset):
        current_time = pygame.time.get_ticks()
        
        # Draw and update afterimages
        new_afterimages = []
        for img, img_x, img_y, spawn_time in self.afterimages:
            age = current_time - spawn_time
            if age < 300: # Afterimage lasts 300ms
                alpha = max(0, 255 - int((age / 300.0) * 255))
                img.set_alpha(alpha)
                screen.blit(img, (img_x - cam_offset[0], img_y - cam_offset[1]))
                new_afterimages.append((img, img_x, img_y, spawn_time))
        self.afterimages = new_afterimages

        # Draw player
        screen_x = self.spaceship_rect.x - cam_offset[0]
        screen_y = self.spaceship_rect.y - cam_offset[1]
        screen.blit(self.spaceship_image, (screen_x, screen_y))

#######################################################################################################################################
#ENTIRE HITBOX BULLSHITTERY
        # --- circle visualisation ---
        cx = self.spaceship_rect.centerx - cam_offset[0]
        cy = self.spaceship_rect.centery - cam_offset[1]

        # Outer glow layers (soft, transparent orange)
        for glow_r, glow_alpha in ((14, 40), (10, 80), (8, 130)):
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*ORANGE, glow_alpha), (glow_r, glow_r), glow_r)
            screen.blit(glow_surf, (cx - glow_r, cy - glow_r))

        # Bright orange core circle
        pygame.draw.circle(screen, ORANGE, (cx, cy), self.hitbox_radius)
        # White pinpoint centre
        pygame.draw.circle(screen, WHITE, (cx, cy), 2)

        # Flash overlay when hit (red tint)
        if current_time < self._hit_flash_until:
            remaining = self._hit_flash_until - current_time
            flash_alpha = min(180, int(remaining / 3))
            flash_surf = pygame.Surface((self.spaceship_rect.width, self.spaceship_rect.height), pygame.SRCALPHA)
            flash_surf.fill((*RED, flash_alpha))
            screen.blit(flash_surf, (screen_x, screen_y))

        # Clear per-frame graze tracking
        self.grazed_this_frame.clear()

    def take_hit(self, damage=1):
        current_time = pygame.time.get_ticks()
        if current_time < self.invincible_until:
            return  # i-frames active
            
        if self.hit_count < self.max_hp:
            self.hit_count += damage
            self._hit_flash_until = current_time + 400  # 400 ms red flash
            self.invincible_until = current_time + 600   # brief post-hit i-frames
            pygame.mixer.Sound(os.path.join("sounds", "hitsound.wav")).play()
                
############################################################################################################################

    def draw_health(self, screen):
        current_hp = self.max_hp - self.hit_count
        if current_hp < 0:
            current_hp = 0

        bar_width = 300
        bar_height = 20
        x_pos = (WIDTH // 2) - (bar_width // 2)
        y_pos = 20
        
        fill_width = (current_hp / self.max_hp) * bar_width

        pygame.draw.rect(screen, RED, (x_pos, y_pos, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (x_pos, y_pos, fill_width, bar_height))
        
        font = pygame.font.SysFont(None, FONT_SMALL)
        hp_text = font.render(f"{current_hp} / {self.max_hp}", True, WHITE)
        text_rect = hp_text.get_rect(center=(WIDTH // 2, y_pos + bar_height // 2))
        screen.blit(hp_text, text_rect)