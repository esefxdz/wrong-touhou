from baddies.base_enemy import BaseEnemy

class Cirno(BaseEnemy):
    """Cirno - Shotgunner enemy that fires blue projectiles."""
    SPRITE_PATH = "cirno.png"
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 4              # Tougher than Rumia
    SPEED = 1.0             # Slightly slower
    FIRE_COOLDOWN = 1500    # Shoots slower
    FIRE_SPEED = 2          # Slower bullets
    FIRE_COLOR = (0, 200, 255) # Cyan/Blue colored bullets
    FIRE_COUNT = 5          # Shotgun spread with 5 pellets
    FIRE_SPREAD_ANGLE = 45  # Spread across 45 degrees
