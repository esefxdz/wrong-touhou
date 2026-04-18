import sys
import os
import pygame
import random
import math
pygame.mixer.init()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import constants
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
    FIRE_COLOR = (255, 0, 0)

    #------------------------------------------
    # shotgun logic / making em shoot multiple bullets
    # target: cirno
    #------------------------------------------
    FIRE_COUNT = 1          # number of bullets per shot
    FIRE_SPREAD_ANGLE = 0   # cone width in degrees

    #------------------------------------------
    # sniper laser stuff / getting sniped across the map
    # target: patchouli
    #------------------------------------------
    IS_SNIPER = False                           # enables lock-on laser + lock behaviour
    FIRE_ON_SCREEN_ONLY = False                 # only fire when visible on screen
    SNIPER_WARN_TIME = 500                      # ms of red lock-on warning before firing
    SNIPER_LASER_TRACK_COLOR = (200, 100, 255)  # thin tracking laser color
    SNIPER_LASER_WARN_COLOR = (255, 50, 50)     # thick warn laser color
    
    #------------------------------------------
    # big tank area / just walking into you doing massive damage
    # target: yukari
    #------------------------------------------
    IS_MELEE = False                            # enables contact damage body slam body blocking
    MELEE_DAMAGE = 1
    
    #------------------------------------------
    # spinner logic / spinning blades that shred you
    # target: sakuya
    #------------------------------------------
    IS_SPINNER = False                          # enables spinning blades that deal contact damage
    SPINNER_BLADE_COUNT = 2
    SPINNER_RADIUS = 80
    SPINNER_SPEED = 0.05
    SPINNER_COLOR = (192, 192, 192)
    SPINNER_BLADE_RADIUS = 15

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
            self.image.fill((255, 0, 255))  # magenta = missing texture
        self.image = pygame.transform.scale(self.image, self.SPRITE_SIZE)
        
        # hitbox
        self.lolrect = pygame.Rect(0, 0, *self.HITBOX_SIZE)
        
        # health
        self.max_hp = self.MAX_HP
        self.hit_count = 0
        self.defeated = False
        
        # shooting
        self.last_fire_time = pygame.time.get_ticks()
        self.fire_cooldown = self.FIRE_COOLDOWN
        self.fire_speed = self.FIRE_SPEED

        # sniper state
        self._locked_angle = None
        self._draw_laser = False
        self._laser_color = self.SNIPER_LASER_TRACK_COLOR
        self._laser_thickness = 1
        self._post_fire_angle = None
        self._post_fire_time = 0
        self._post_fire_duration = 300  # the beam disappear timing
        
        # spinner state
        if self.IS_SPINNER:
            self.spinner_angle = 0.0
            
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
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = player_x + random.randint(-constants.WIDTH // 2, constants.WIDTH // 2)
            y = player_y - constants.HEIGHT // 2 - margin
        elif side == 'bottom':
            x = player_x + random.randint(-constants.WIDTH // 2, constants.WIDTH // 2)
            y = player_y + constants.HEIGHT // 2 + margin
        elif side == 'left':
            x = player_x - constants.WIDTH // 2 - margin
            y = player_y + random.randint(-constants.HEIGHT // 2, constants.HEIGHT // 2)
        else:
            x = player_x + constants.WIDTH // 2 + margin
            y = player_y + random.randint(-constants.HEIGHT // 2, constants.HEIGHT // 2)
        x = max(0, min(x, self.player.map_w))
        y = max(0, min(y, self.player.map_h))
        self.lolrect.topleft = (x, y)
    
    def _is_on_screen(self, cam_offset):
        sx = self.lolrect.centerx - cam_offset[0]
        sy = self.lolrect.centery - cam_offset[1]
        return -50 <= sx <= constants.WIDTH + 50 and -50 <= sy <= constants.HEIGHT + 50

    #------------------------------------------
    # firing system / deciding how they shoot
    # target: @everyone
    #------------------------------------------
    def fire(self, proj_manager, cam_offset=(0, 0)):
        if self.defeated:
            return
        current_time = pygame.time.get_ticks()
        time_since = current_time - self.last_fire_time

        # --- On-screen gate: stall cooldown while off screen ---
        if self.FIRE_ON_SCREEN_ONLY and not self._is_on_screen(cam_offset):
            if time_since > self.FIRE_COOLDOWN - 1000:
                self.last_fire_time = current_time - (self.FIRE_COOLDOWN - 1000)
            self._draw_laser = False
            return

        #------------------------------------------
        # sniper lock-on logic / checking angles
        # target: patchouli
        #------------------------------------------
        if self.IS_SNIPER:
            px, py = self.player.spaceship_rect.center
            dx = px - self.lolrect.centerx
            dy = py - self.lolrect.centery
            # Always track player - no warning phase
            self._locked_angle = math.atan2(dy, dx)
            self._draw_laser = True

            if time_since > self.FIRE_COOLDOWN:
                # Store the shot angle for the fading beam visual
                self._post_fire_angle = self._locked_angle
                self._post_fire_time = current_time
                fire_dx = math.cos(self._locked_angle)
                fire_dy = math.sin(self._locked_angle)
                proj_manager.spawn(
                    self.lolrect.centerx, self.lolrect.centery,
                    fire_dx, fire_dy, self.fire_speed,
                    radius=8, color=self.FIRE_COLOR, type_id=0, owner=1, angle=self._locked_angle
                )
                self.last_fire_time = current_time
            return


        #------------------------------------------
        # normal fire / shotgun shooting
        # target: @everyone
        #------------------------------------------
        if time_since > self.fire_cooldown:
            self.last_fire_time = current_time
            enemy_x, enemy_y = self.lolrect.center
            player_x, player_y = self.player.spaceship_rect.center
            dx = player_x - enemy_x
            dy = player_y - enemy_y
            distance = math.hypot(dx, dy) or 1
            base_angle = math.atan2(dy, dx)

            for i in range(self.FIRE_COUNT):
                if self.FIRE_COUNT <= 1:
                    angle_offset = 0
                else:
                    fraction = i / (self.FIRE_COUNT - 1)
                    angle_offset = math.radians(self.FIRE_SPREAD_ANGLE * (fraction - 0.5))
                fire_angle = base_angle + angle_offset
                proj_manager.spawn(
                    enemy_x, enemy_y,
                    math.cos(fire_angle), math.sin(fire_angle), self.fire_speed,
                    radius=5, color=self.FIRE_COLOR, type_id=0, owner=1, angle=fire_angle
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
    
    def move_toward_player(self):
        enemy_x = self.lolrect.centerx
        enemy_y = self.lolrect.centery
        player_x = self.player.spaceship_rect.centerx
        player_y = self.player.spaceship_rect.centery
        
        dx = player_x - enemy_x
        dy = player_y - enemy_y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return
        
        dx = dx / distance
        dy = dy / distance
        self.lolrect.x += dx * self.SPEED
        self.lolrect.y += dy * self.SPEED
    
    #------------------------------------------
    # main update loop / running all the math
    # target: @everyone
    #------------------------------------------
    #------------------------------------------
    # spinner physics / spinning the blades around
    # target: sakuya
    #------------------------------------------
    def update_spinner(self, player):
        self.spinner_angle += self.SPINNER_SPEED
        px, py = player.spaceship_rect.center
        player_r = 25 # spaceship rect fits in 50x50 physically
        
        for i in range(self.SPINNER_BLADE_COUNT):
            angle = self.spinner_angle + (i * 2 * math.pi / self.SPINNER_BLADE_COUNT)
            bx = self.lolrect.centerx + math.cos(angle) * self.SPINNER_RADIUS
            by = self.lolrect.centery + math.sin(angle) * self.SPINNER_RADIUS
            
            # Simple circular contact damage against player
            if math.hypot(bx - px, by - py) < (self.SPINNER_BLADE_RADIUS + player_r):
                player.take_hit()
                
    def update(self, screen, player, proj_manager):
        if not self.defeated:
            self.move_toward_player()
            if self.IS_SPINNER:
                self.update_spinner(player)
            
            #------------------------------------------
            # tank contact damage / hitting you with their body
            # target: yukari
            #------------------------------------------
            if self.IS_MELEE:
                # Add base collision shape overlap evaluation
                if self.lolrect.colliderect(player.spaceship_rect):
                    player.take_hit(damage=self.MELEE_DAMAGE)
            cam_offset = player.get_camera_offset()
            self.fire(proj_manager, cam_offset)

    #------------------------------------------
    # master drawing area / slapping all their sprites on screen
    # target: @everyone
    #------------------------------------------
    def draw(self, screen, cam_offset):
        if self.defeated:
            return

        #------------------------------------------
        # rendering laser sights
        # target: patchouli
        #------------------------------------------
        if self.IS_SNIPER:
            current_time = pygame.time.get_ticks()
            sx = self.lolrect.centerx - cam_offset[0]
            sy = self.lolrect.centery - cam_offset[1]

            # Draw the post-fire thick fading beam
            if self._post_fire_angle is not None:
                age = current_time - self._post_fire_time
                if age < self._post_fire_duration:
                    t = 1.0 - (age / self._post_fire_duration)  # 1.0 -> 0.0
                    thickness = max(1, int(24 * t))
                    r, g, b = self.FIRE_COLOR
                    ex = sx + math.cos(self._post_fire_angle) * 2000
                    ey = sy + math.sin(self._post_fire_angle) * 2000
                    pygame.draw.line(screen, (r, g, b), (int(sx), int(sy)), (int(ex), int(ey)), thickness)
                else:
                    self._post_fire_angle = None

            # Draw thin tracking laser
            if self._draw_laser and self._locked_angle is not None:
                ex = sx + math.cos(self._locked_angle) * 2000
                ey = sy + math.sin(self._locked_angle) * 2000
                pygame.draw.line(screen, self.SNIPER_LASER_TRACK_COLOR, (int(sx), int(sy)), (int(ex), int(ey)), 1)

        #------------------------------------------
        # rendering spinning blades
        # target: sakuya
        #------------------------------------------
        if self.IS_SPINNER:
            for i in range(self.SPINNER_BLADE_COUNT):
                angle = self.spinner_angle + (i * 2 * math.pi / self.SPINNER_BLADE_COUNT)
                bx = self.lolrect.centerx + math.cos(angle) * self.SPINNER_RADIUS
                by = self.lolrect.centery + math.sin(angle) * self.SPINNER_RADIUS
                pygame.draw.circle(screen, self.SPINNER_COLOR, 
                                   (int(bx - cam_offset[0]), int(by - cam_offset[1])), 
                                   self.SPINNER_BLADE_RADIUS)

        # Draw sprite
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
        
        # Draw red background
        pygame.draw.rect(screen, (255, 0, 0), (bx, by, bar_w, bar_h))
        # Draw green health fill
        if fill_w > 0:
            pygame.draw.rect(screen, (0, 255, 0), (bx, by, fill_w, bar_h))
        #--------------------------------------------------------