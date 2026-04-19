from baddies.base_enemy import BaseEnemy

class Yukari(BaseEnemy):
    """Yukari - Tank enemy that body-slams you for massive damage."""

    #------------------------------------------
    # tank config / her stats and melee settings
    #------------------------------------------
    SPRITE_PATH = "yukari.png"
    SPRITE_SIZE = (200, 200)  # big physical presence
    HITBOX_SIZE = (100, 100)  # large impact block
    MAX_HP = 25               # heavy bullet sponge
    SPEED = 0.5               # slow but inevitable
    FIRE_COOLDOWN = 999999    # she doesn't shoot standard bullets
    MELEE_DAMAGE = 2          # hits very hard per contact

    #------------------------------------------
    # drop table / absolute tank, highest reward in the game
    #------------------------------------------
    DROP_XP_RANGE = (8, 14)  # 8-14 XP orbs per kill
    DROP_HP_RANGE  = (1, 3)  # 1-3 HP orbs, always drops at least one

    #------------------------------------------
    # melee update override / body slam contact damage
    #------------------------------------------
    def update(self, screen, player, proj_manager):
        if self.defeated:
            return
        
        self.move_toward_player()
        
        # slam damage when her body overlaps the player rect
        if self.lolrect.colliderect(player.spaceship_rect):
            player.take_hit(damage=self.MELEE_DAMAGE)