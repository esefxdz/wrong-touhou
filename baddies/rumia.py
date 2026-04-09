from baddies.base_enemy import BaseEnemy

class Rumia(BaseEnemy):
    """Rumia - basic chaser enemy that fires at player."""
    SPRITE_PATH = "rumia.png"
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 2
    SPEED = 1.5
    FIRE_COOLDOWN = 1000
    FIRE_SPEED = 3
    FIRE_COLOR = (255, 0, 0)
