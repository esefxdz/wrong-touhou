from baddies.base_enemy import BaseEnemy

class Yukari(BaseEnemy):
    """Yukari - Tank enemy that body-slams you for massive damage."""
    SPRITE_PATH = "yukari.png"
    SPRITE_SIZE = (200, 200) # Big physical presence
    HITBOX_SIZE = (100, 100) # Large impact block
    MAX_HP = 25              # Heavy bullet sponge
    SPEED = 0.5              # Slow but inevitable
    
    FIRE_COUNT = 0           # She doesn't shoot standard bullets
    
    IS_MELEE = True          # She attacks by running into you
    MELEE_DAMAGE = 2         # Hits very hard