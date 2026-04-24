import sys
import os
import pygame
import random
import math
pygame.mixer.init()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from constants import RED, GREEN, WHITE, MAGENTA, WIDTH, HEIGHT


# ─────────────────────────────────────────────────────────────────────────────
# Orb
# A single pickupable orb sitting in world space.
# type_: "xp" or "hp"
# ─────────────────────────────────────────────────────────────────────────────
class Orb:
    PICKUP_RADIUS  = 30   # how close the player must be to collect
    MAGNET_RADIUS  = 150  # orbs slide toward the player when within this range
    MAGNET_SPEED   = 4    # pixels per frame when magnetising
    FLOAT_SPEED    = 0.04 # gentle bob frequency
    FLOAT_AMP      = 3    # bob height in pixels

    # visual radii and colours per type
    _STYLE = {
        "xp": {"radius": 7,  "color": (80, 220, 255),  "glow": (30, 120, 200)},
        "hp": {"radius": 8,  "color": (50, 255, 50),   "glow": (20, 180, 20)},
    }

    def __init__(self, x, y, type_):
        self.x     = float(x)
        self.y     = float(y)
        self.type_ = type_
        self.collected = False
        self._age  = random.uniform(0, 6.28)  # phase-offset so orbs don't all bob in sync

    def update(self, player, current_map, force_magnet=False):
        if self.collected:
            return

        px, py = player.spaceship_rect.center
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)

        # slide toward player when within magnet range (faster the closer they are)
        if force_magnet or (dist < self.MAGNET_RADIUS and dist > 0):
            # If wave ended, yank them extremely fast from anywhere on the map
            base_speed = self.MAGNET_SPEED * 10 if force_magnet else self.MAGNET_SPEED
            speed = base_speed * (1 + max(0, self.MAGNET_RADIUS - dist) / self.MAGNET_RADIUS)
            
            self.x += (dx / dist) * speed
            # don't magnet Y aggressively if we want it to stay on ground, but let's just let magnet override gravity
            self.y += (dy / dist) * speed
            dist = math.hypot(px - self.x, py - self.y)  # recalc after move
        else:
            # Gravity
            self.velocity_y = getattr(self, 'velocity_y', 0)
            self.velocity_y += current_map.GRAVITY
            self.y += self.velocity_y
            
            r = self._STYLE.get(self.type_, self._STYLE["xp"])["radius"]
            for rx, ry, rw, rh in current_map.COLLISION_RECTS:
                if (rx <= self.x <= rx + rw) and (ry <= self.y + r <= ry + rh):
                    if self.velocity_y > 0:
                        self.y = ry - r
                        self.velocity_y = 0

        # collected when close enough to the player's hitbox
        if dist < self.PICKUP_RADIUS:
            self.collected = True
            if self.type_ == "xp":
                player.level_system.add_xp(3)
            elif self.type_ == "hp":
                # heal 1 point, never over max
                player.hit_count = max(0, player.hit_count - 1)

        self._age += self.FLOAT_SPEED

    def draw(self, screen, cam_offset):
        if self.collected:
            return

        style = self._STYLE.get(self.type_, self._STYLE["xp"])
        r     = style["radius"]
        color = style["color"]
        glow_color = style["glow"]

        # If XP orb, calculate dynamic rainbow colors
        if self.type_ == "xp":
            import colorsys
            hue = ((pygame.time.get_ticks() / 1500.0) + self._age) % 1.0 
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            glow_rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.6)
            glow_color = (int(glow_rgb[0] * 255), int(glow_rgb[1] * 255), int(glow_rgb[2] * 255))

        # screen position with gentle vertical bob
        sx = int(self.x - cam_offset[0])
        sy = int(self.y - cam_offset[1] + math.sin(self._age) * self.FLOAT_AMP)

        # soft glow ring
        glow_surf = pygame.Surface((r * 5, r * 5), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*glow_color, 60), (r * 5 // 2, r * 5 // 2), r * 2)
        screen.blit(glow_surf, (sx - r * 5 // 2, sy - r * 5 // 2))

        # bright core
        pygame.draw.circle(screen, color, (sx, sy), r)
        # white specular glint
        pygame.draw.circle(screen, WHITE, (sx, sy), max(1, r // 3))


class BaseEnemy:
    """Base class for all enemies. Subclass this and override the config to create new enemies."""
    
    #------------------------------------------
    # common enemy stats / the basic stuff
    # target: @everyone
    #------------------------------------------
    SPRITE_PATH = None      # path to sprite image relative to baddies folder
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 2
    SPEED = 1.5
    FIRE_COOLDOWN = 1000    # ms between shots
    FIRE_SPEED = 3          # bullet travel speed
    FIRE_COLOR = RED
    
    GRAVITY_MULTIPLIER = 1.0 # Multiplier of map gravity
    JUMP_STRENGTH = -10.0
    IS_FLYING = False

    #------------------------------------------
    # drop tables / subclasses set these to control loot
    # store as (min, max) inclusive — randint is rolled fresh on each kill
    # target: @everyone
    #------------------------------------------
    DROP_XP_RANGE = (0, 0)   # how many XP orbs this enemy can drop
    DROP_HP_RANGE  = (0, 0)  # how many HP orbs this enemy can drop

    #------------------------------------------
    # game initialization area / hooking up the basics
    # target: @everyone
    #------------------------------------------
    def __init__(self, player_ref):
        self.player = player_ref
        
        # load sprite
        if self.SPRITE_PATH:
            image_path = os.path.join(os.path.dirname(__file__), self.SPRITE_PATH)
            self.image = pygame.image.load(image_path)
        else:
            self.image = pygame.Surface(self.SPRITE_SIZE)
            self.image.fill(MAGENTA)  # magenta = missing texture
        self.image = pygame.transform.scale(self.image, self.SPRITE_SIZE)
        
        # hitbox
        self.lolrect = pygame.Rect(0, 0, *self.HITBOX_SIZE)
        
        # health
        self.max_hp = self.MAX_HP
        self.hit_count = 0
        self.defeated = False

        # orbs waiting to be picked up — populated in take_hit when the enemy dies
        self.dropped_orbs: list[Orb] = []
        
        # shooting
        self.last_fire_time = pygame.time.get_ticks()
        self.fire_cooldown = self.FIRE_COOLDOWN
        self.fire_speed = self.FIRE_SPEED
        
        # platformer jumping/gravity
        self.velocity_y = 0.0
            
        # spawn
        self.spawn_outside_screen()
    
    #------------------------------------------
    # map spawning stuff / dropping them outside the screen
    # target: @everyone
    #------------------------------------------
    def spawn_outside_screen(self):
        player_x = self.player.spaceship_rect.centerx
        player_y = self.player.spaceship_rect.centery
        margin = 200
        side = random.choice(['top', 'left', 'right'])
        if side == 'top':
            x = player_x + random.randint(-WIDTH // 2, WIDTH // 2)
            y = player_y - HEIGHT // 2 - margin
        elif side == 'bottom':
            x = player_x + random.randint(-WIDTH // 2, WIDTH // 2)
            y = player_y + HEIGHT // 2 + margin
        elif side == 'left':
            x = player_x - WIDTH // 2 - margin
            y = player_y + random.randint(-HEIGHT // 2, HEIGHT // 2)
        else:
            x = player_x + WIDTH // 2 + margin
            y = player_y + random.randint(-HEIGHT // 2, HEIGHT // 2)
        x = max(0, min(x, self.player.map_w))
        y = max(0, min(y, self.player.map_h))
        self.lolrect.topleft = (x, y)
    
    def _is_on_screen(self, cam_offset):
        sx = self.lolrect.centerx - cam_offset[0]
        sy = self.lolrect.centery - cam_offset[1]
        return -50 <= sx <= WIDTH + 50 and -50 <= sy <= HEIGHT + 50

    #------------------------------------------
    # firing system / single bullet aimed at player
    # target: @everyone
    #------------------------------------------
    def fire(self, proj_manager, cam_offset=(0, 0)):
        if self.defeated:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire_time > self.fire_cooldown:
            self.last_fire_time = current_time
            enemy_x, enemy_y = self.lolrect.center
            player_x, player_y = self.player.spaceship_rect.center
            dx = player_x - enemy_x
            dy = player_y - enemy_y
            distance = math.hypot(dx, dy) or 1
            angle = math.atan2(dy, dx)
            proj_manager.spawn(
                enemy_x, enemy_y,
                dx / distance, dy / distance, self.fire_speed,
                radius=5, color=self.FIRE_COLOR, type_id=0, owner=1, angle=angle
            )

    #------------------------------------------
    # health and movement / taking damage and chasing player
    # target: @everyone
    #------------------------------------------
    def take_hit(self):
        if not self.defeated:
            self.hit_count += 1
            pygame.mixer.Sound(os.path.join("sounds", "hitsound.wav")).play()
            if self.hit_count >= self.max_hp:
                self.defeated = True
                self.player.enemies_killed += 1
                pygame.mixer.Sound(os.path.join("sounds", "killsound.wav")).play()

                # roll drop counts fresh per kill using the subclass range
                xp_count = random.randint(*self.DROP_XP_RANGE)
                hp_count = random.randint(*self.DROP_HP_RANGE)
                cx, cy = self.lolrect.center
                for _ in range(xp_count):
                    ox = cx + random.randint(-20, 20)
                    oy = cy + random.randint(-20, 20)
                    self.dropped_orbs.append(Orb(ox, oy, "xp"))
                for _ in range(hp_count):
                    ox = cx + random.randint(-20, 20)
                    oy = cy + random.randint(-20, 20)
                    self.dropped_orbs.append(Orb(ox, oy, "hp"))
    
    def move_toward_player(self, current_map):
        enemy_x = self.lolrect.centerx
        enemy_y = self.lolrect.centery
        player_x = self.player.spaceship_rect.centerx
        player_y = self.player.spaceship_rect.centery
        
        dx = player_x - enemy_x
        dy = player_y - enemy_y
        
        if self.IS_FLYING:
            distance = math.hypot(dx, dy)
            if distance > 0:
                self.lolrect.x += (dx / distance) * self.SPEED
                self.lolrect.y += (dy / distance) * self.SPEED
            return
            
        # Ground movement
        # Horizontal
        speed = self.SPEED
        h_dir = 1 if dx > 0 else -1 if dx < 0 else 0
        h_vel = h_dir * speed
        self.lolrect.x += h_vel
        
        for rx, ry, rw, rh in current_map.COLLISION_RECTS:
            rect = pygame.Rect(rx, ry, rw, rh)
            if self.lolrect.colliderect(rect):
                if h_vel > 0: self.lolrect.right = rect.left
                if h_vel < 0: self.lolrect.left = rect.right
                    
        # Vertical (Gravity)
        gravity = current_map.GRAVITY * self.GRAVITY_MULTIPLIER
        self.velocity_y += gravity
        self.lolrect.y += self.velocity_y
        
        for rx, ry, rw, rh in current_map.COLLISION_RECTS:
            rect = pygame.Rect(rx, ry, rw, rh)
            if self.lolrect.colliderect(rect):
                if self.velocity_y > 0:
                    self.lolrect.bottom = rect.top
                    self.velocity_y = 0
                elif self.velocity_y < 0:
                    self.lolrect.top = rect.bottom
                    self.velocity_y = 0

    #------------------------------------------
    # orb lifecycle / called from main loop after enemy.update / enemy.draw
    # target: @everyone
    #------------------------------------------
    def update_orbs(self, player, current_map, force_magnet=False):
        """Tick every live orb; remove ones that have been collected."""
        self.dropped_orbs = [o for o in self.dropped_orbs if not o.collected]
        for orb in self.dropped_orbs:
            orb.update(player, current_map, force_magnet)

    def draw_orbs(self, screen, cam_offset):
        """Draw every live orb belonging to this enemy."""
        for orb in self.dropped_orbs:
            orb.draw(screen, cam_offset)
    
    #------------------------------------------
    # main update loop / running all the math
    # target: @everyone
    #------------------------------------------
    def update(self, screen, player, proj_manager, current_map):
        if not self.defeated:
            self.move_toward_player(current_map)
            cam_offset = player.get_camera_offset()
            self.fire(proj_manager, cam_offset)

    #------------------------------------------
    # master drawing area / slapping all their sprites on screen
    # target: @everyone
    #------------------------------------------
    def draw(self, screen, cam_offset):
        if self.defeated:
            return

        # draw sprite
        image_rect = self.image.get_rect(center=self.lolrect.center)
        screen.blit(self.image, (image_rect.x - cam_offset[0], image_rect.y - cam_offset[1]))

        #------------------------------------------
        # little healthbars on top of their heads
        # target: @everyone
        #------------------------------------------
        current_hp = self.max_hp - self.hit_count
        bar_w = min(self.lolrect.width, 50)
        bar_h = 6
        hp_ratio = max(0.0, current_hp / self.max_hp)
        fill_w = int(bar_w * hp_ratio)
        
        bx = self.lolrect.centerx - cam_offset[0] - (bar_w // 2)
        by = self.lolrect.top - cam_offset[1] - 15
        
        # red background then green health fill
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        if fill_w > 0:
            pygame.draw.rect(screen, GREEN, (bx, by, fill_w, bar_h))