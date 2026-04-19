import math
import pygame
from baddies.base_enemy import BaseEnemy
from constants import SILVER

class Sakuya(BaseEnemy):
    """Sakuya - Spinner enemy with orbiting blades that tries to physically hit you."""

    #------------------------------------------
    # spinner config / her stats and blade settings
    #------------------------------------------
    SPRITE_PATH = "sakuya.png"
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 5
    SPEED = 2.0
    FIRE_COOLDOWN = 999999  # she doesn't shoot standard bullets
    SPINNER_BLADE_COUNT = 2
    SPINNER_RADIUS = 90     # orbit distance from center
    SPINNER_SPEED = 0.08    # rotation speed in radians per frame
    SPINNER_COLOR = SILVER  # silver knives
    SPINNER_BLADE_RADIUS = 15        # threat size per blade

    #------------------------------------------
    # drop table / fast and dangerous, rewarding to kill
    #------------------------------------------
    DROP_XP_RANGE = (4, 7)   # 4-7 XP orbs per kill
    DROP_HP_RANGE  = (0, 2)  # 0-2 HP orbs

    def __init__(self, player_ref):
        super().__init__(player_ref)
        
        # blade rotation tracker
        self.spinner_angle = 0.0

    #------------------------------------------
    # spinner update override / rotating blades + contact damage
    #------------------------------------------
    def update(self, screen, player, proj_manager):
        if self.defeated:
            return
        
        self.move_toward_player()
        
        # spin the blades and check if they clip the player
        self.spinner_angle += self.SPINNER_SPEED
        px, py = player.spaceship_rect.center
        player_r = 25  # spaceship fits in ~50x50
        
        for i in range(self.SPINNER_BLADE_COUNT):
            angle = self.spinner_angle + (i * 2 * math.pi / self.SPINNER_BLADE_COUNT)
            bx = self.lolrect.centerx + math.cos(angle) * self.SPINNER_RADIUS
            by = self.lolrect.centery + math.sin(angle) * self.SPINNER_RADIUS
            if math.hypot(bx - px, by - py) < (self.SPINNER_BLADE_RADIUS + player_r):
                player.take_hit()

    #------------------------------------------
    # spinner draw override / rendering the blades around her
    #------------------------------------------
    def draw(self, screen, cam_offset):
        if self.defeated:
            return

        # draw orbiting blades first so they appear behind/around sprite
        for i in range(self.SPINNER_BLADE_COUNT):
            angle = self.spinner_angle + (i * 2 * math.pi / self.SPINNER_BLADE_COUNT)
            bx = self.lolrect.centerx + math.cos(angle) * self.SPINNER_RADIUS
            by = self.lolrect.centery + math.sin(angle) * self.SPINNER_RADIUS
            pygame.draw.circle(screen, self.SPINNER_COLOR,
                               (int(bx - cam_offset[0]), int(by - cam_offset[1])),
                               self.SPINNER_BLADE_RADIUS)

        # sprite and healthbar from base
        super().draw(screen, cam_offset)