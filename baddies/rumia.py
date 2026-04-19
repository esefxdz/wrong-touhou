from baddies.base_enemy import BaseEnemy
from constants import RED

class Rumia(BaseEnemy):
    """Rumia - basic chaser enemy that fires at player."""
    SPRITE_PATH = "rumia.png"
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 2
    SPEED = 1.5
    FIRE_COOLDOWN = 1000
    FIRE_SPEED = 3
    FIRE_COLOR = RED

    #------------------------------------------
    # drop table / she's weak so drops are minimal
    #------------------------------------------
    DROP_XP_RANGE = (1, 3)   # 1-3 XP orbs per kill
    DROP_HP_RANGE  = (0, 0)  # no health drops
