import pygame
import os
import math
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from constants import WIDTH, HEIGHT, ORANGE, WHITE, RED, GREEN, FONT_SMALL
from player_files.level import LevelSystem

class BasePlayer:
    """Base class for all playable characters. Subclass and override configs to make new ones."""

    #------------------------------------------
    # character config / subclasses set these
    # target: @everyone
    #------------------------------------------
    NAME        = "Unknown"
    DESCRIPTION = "No description."
    PORTRAIT_PATH = None        # path relative to player_files/ for the selection screen

    SPRITE_PATH   = None        # spritesheet path relative to player_files/
    SPRITE_SIZE   = (64, 64)    # size of a single frame on the sheet
    FRAME_COUNT   = 1           # total horizontal frames on the sheet
    FRAME_SPEED   = 150         # ms per frame

    HITBOX_SIZE   = (50, 50)
    MAX_HP        = 5
    PLAYER_SPEED  = 10
    BULLET_SPEED  = 25
    SHOOT_COOLDOWN = 75

    HITBOX_RADIUS = 6
    GRAZE_RADIUS  = 28

    JUMP_STRENGTH    = -12.0
    DASH_COOLDOWN    = 1000
    DASH_DURATION    = 200
    DASH_MULTIPLIER  = 3.5

    #------------------------------------------
    # initialization / loading sprites and setting defaults
    # target: @everyone
    #------------------------------------------
    def __init__(self, x, y, map_w=3000, map_h=3000):
        self.map_w = map_w
        self.map_h = map_h

        # sprite / animation setup
        if self.SPRITE_PATH:
            sheet_path = os.path.join(os.path.dirname(__file__), self.SPRITE_PATH)
            sheet = pygame.image.load(sheet_path).convert_alpha()
            fw, fh = self.SPRITE_SIZE
            self.frames = [
                pygame.transform.scale(
                    sheet.subsurface(pygame.Rect(i * fw, 0, fw, fh)),
                    self.SPRITE_SIZE
                )
                for i in range(self.FRAME_COUNT)
            ]
        else:
            surf = pygame.Surface(self.SPRITE_SIZE, pygame.SRCALPHA)
            surf.fill((200, 200, 200))
            self.frames = [surf]

        self._frame_idx   = 0
        self._last_frame  = pygame.time.get_ticks()
        self.spaceship_image = self.frames[0]

        # rect / hitbox
        self.spaceship_rect = self.spaceship_image.get_rect()
        self.spaceship_rect.center = (map_w // 2, map_h // 2)

        # stats
        self.max_hp       = self.MAX_HP
        self.hit_count    = 0
        self.enemies_killed = 0
        self.damage_dealt   = 0
        self.bullet_speed   = self.BULLET_SPEED
        self.shoot_cooldown = self.SHOOT_COOLDOWN
        self.last_shot_time = pygame.time.get_ticks()
        self.player_speed   = self.PLAYER_SPEED

        # hitbox circles
        self.hitbox_radius = self.HITBOX_RADIUS
        self.graze_radius  = self.GRAZE_RADIUS

        # platformer physics
        self.velocity_y   = 0.0
        self.jump_strength = self.JUMP_STRENGTH

        # dash / iframe
        self.is_dashing          = False
        self.dash_cooldown       = self.DASH_COOLDOWN
        self.last_dash_time      = 0
        self.dash_duration       = self.DASH_DURATION
        self.dash_speed_multiplier = self.DASH_MULTIPLIER
        self.dash_dir            = (0, 0)
        self.invincible_until    = 0
        self.afterimages         = []

        # hit flash
        self._hit_flash_until = 0

        # graze
        self.grazed_this_frame: set = set()

        # level system
        self.level_system = LevelSystem()

    #------------------------------------------
    # animation / advance frames over time
    # target: @everyone
    #------------------------------------------
    def _tick_animation(self):
        now = pygame.time.get_ticks()
        if now - self._last_frame >= self.FRAME_SPEED:
            self._frame_idx    = (self._frame_idx + 1) % len(self.frames)
            self.spaceship_image = self.frames[self._frame_idx]
            self._last_frame   = now

    #------------------------------------------
    # movement / dash + platformer physics
    # target: @everyone
    #------------------------------------------
    def move(self, keys, current_map):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        if self.is_dashing:
            if current_time - self.last_dash_time > self.dash_duration:
                self.is_dashing = False
            else:
                self.spaceship_rect.x += self.dash_dir[0] * self.player_speed * self.dash_speed_multiplier
                for rx, ry, rw, rh in current_map.COLLISION_RECTS:
                    rect = pygame.Rect(rx, ry, rw, rh)
                    if self.spaceship_rect.colliderect(rect):
                        if self.dash_dir[0] > 0: self.spaceship_rect.right = rect.left
                        elif self.dash_dir[0] < 0: self.spaceship_rect.left = rect.right

                self.spaceship_rect.y += self.dash_dir[1] * self.player_speed * self.dash_speed_multiplier
                self.velocity_y = 0
                for rx, ry, rw, rh in current_map.COLLISION_RECTS:
                    rect = pygame.Rect(rx, ry, rw, rh)
                    if self.spaceship_rect.colliderect(rect):
                        if self.dash_dir[1] > 0: self.spaceship_rect.bottom = rect.top
                        elif self.dash_dir[1] < 0: self.spaceship_rect.top = rect.bottom

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

#######################################################################################################################################
#PLATFORMER PHYSICS BULLSHITTERY

        grav = current_map.GRAVITY

        dx = 0
        if keys[pygame.K_a]: dx -= self.player_speed
        if keys[pygame.K_d]: dx += self.player_speed

        self.spaceship_rect.x += dx
        for rx, ry, rw, rh in current_map.COLLISION_RECTS:
            rect = pygame.Rect(rx, ry, rw, rh)
            if self.spaceship_rect.colliderect(rect):
                if dx > 0: self.spaceship_rect.right = rect.left
                if dx < 0: self.spaceship_rect.left = rect.right

        self.spaceship_rect.x = max(0, min(self.spaceship_rect.x, self.map_w - self.spaceship_rect.width))

        self.velocity_y += grav
        self.spaceship_rect.y += self.velocity_y

        on_ground = False
        for rx, ry, rw, rh in current_map.COLLISION_RECTS:
            rect = pygame.Rect(rx, ry, rw, rh)
            if self.spaceship_rect.colliderect(rect):
                if self.velocity_y > 0:
                    self.spaceship_rect.bottom = rect.top
                    self.velocity_y = 0
                    on_ground = True
                elif self.velocity_y < 0:
                    self.spaceship_rect.top = rect.bottom
                    self.velocity_y = 0

        if self.spaceship_rect.bottom > self.map_h:
            self.spaceship_rect.bottom = self.map_h
            self.velocity_y = 0
            on_ground = True
        if self.spaceship_rect.top < 0:
            self.spaceship_rect.top = 0
            self.velocity_y = 0

        if on_ground and keys[pygame.K_w]:
            self.velocity_y = self.jump_strength

#######################################################################################################################################

    #------------------------------------------
    # camera / centers on player clamped to map
    # target: @everyone
    #------------------------------------------
    def get_camera_offset(self):
        cam_x = self.spaceship_rect.centerx - WIDTH // 2
        cam_y = self.spaceship_rect.centery - HEIGHT // 2
        cam_x = max(0, min(cam_x, self.map_w - WIDTH))
        cam_y = max(0, min(cam_y, self.map_h - HEIGHT))
        return cam_x, cam_y

    #------------------------------------------
    # shooting / fires toward mouse cursor
    # target: @everyone
    #------------------------------------------
    def shoot(self, cam_offset, proj_manager):
        current_time = pygame.time.get_ticks()
        if pygame.key.get_pressed()[pygame.K_SPACE] and current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_world_x = mouse_x + cam_offset[0]
            mouse_world_y = mouse_y + cam_offset[1]
            px, py = self.spaceship_rect.center
            dx = mouse_world_x - px
            dy = mouse_world_y - py
            dist = math.hypot(dx, dy) or 1
            direction = (dx / dist, dy / dist)
            angle = math.atan2(direction[1], direction[0])
            proj_manager.spawn(
                px, py, direction[0], direction[1], self.bullet_speed,
                radius=10, color=WHITE, type_id=1, owner=0, angle=angle
            )

    #------------------------------------------
    # drawing / sprite + hitbox + afterimages
    # target: @everyone
    #------------------------------------------
    def draw(self, screen, cam_offset):
        current_time = pygame.time.get_ticks()
        self._tick_animation()

        # afterimages
        new_afterimages = []
        for img, img_x, img_y, spawn_time in self.afterimages:
            age = current_time - spawn_time
            if age < 300:
                alpha = max(0, 255 - int((age / 300.0) * 255))
                img.set_alpha(alpha)
                screen.blit(img, (img_x - cam_offset[0], img_y - cam_offset[1]))
                new_afterimages.append((img, img_x, img_y, spawn_time))
        self.afterimages = new_afterimages

        screen_x = self.spaceship_rect.x - cam_offset[0]
        screen_y = self.spaceship_rect.y - cam_offset[1]
        screen.blit(self.spaceship_image, (screen_x, screen_y))

#######################################################################################################################################
#ENTIRE HITBOX BULLSHITTERY
        cx = self.spaceship_rect.centerx - cam_offset[0]
        cy = self.spaceship_rect.centery - cam_offset[1]

        for glow_r, glow_alpha in ((14, 40), (10, 80), (8, 130)):
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*ORANGE, glow_alpha), (glow_r, glow_r), glow_r)
            screen.blit(glow_surf, (cx - glow_r, cy - glow_r))

        pygame.draw.circle(screen, ORANGE, (cx, cy), self.hitbox_radius)
        pygame.draw.circle(screen, WHITE, (cx, cy), 2)

        if current_time < self._hit_flash_until:
            remaining = self._hit_flash_until - current_time
            flash_alpha = min(180, int(remaining / 3))
            flash_surf = pygame.Surface((self.spaceship_rect.width, self.spaceship_rect.height), pygame.SRCALPHA)
            flash_surf.fill((*RED, flash_alpha))
            screen.blit(flash_surf, (screen_x, screen_y))

        self.grazed_this_frame.clear()

############################################################################################################################

    #------------------------------------------
    # damage / taking hits with i-frame support
    # target: @everyone
    #------------------------------------------
    def take_hit(self, damage=1):
        current_time = pygame.time.get_ticks()
        if current_time < self.invincible_until:
            return
        if self.hit_count < self.max_hp:
            self.hit_count += damage
            self._hit_flash_until = current_time + 400
            self.invincible_until = current_time + 600
            pygame.mixer.Sound(os.path.join("sounds", "hitsound.wav")).play()

    #------------------------------------------
    # health bar / drawn at top of screen
    # target: @everyone
    #------------------------------------------
    def draw_health(self, screen):
        current_hp = max(0, self.max_hp - self.hit_count)
        bar_width  = 300
        bar_height = 20
        x_pos = (WIDTH // 2) - (bar_width // 2)
        y_pos = 20
        fill_width = (current_hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, RED,   (x_pos, y_pos, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (x_pos, y_pos, fill_width, bar_height))
        font = pygame.font.SysFont(None, FONT_SMALL)
        hp_text = font.render(f"{current_hp} / {self.max_hp}", True, WHITE)
        screen.blit(hp_text, hp_text.get_rect(center=(WIDTH // 2, y_pos + bar_height // 2)))
