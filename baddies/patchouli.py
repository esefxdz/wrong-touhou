from baddies.base_enemy import BaseEnemy

class Patchouli(BaseEnemy):
    """Patchouli - Sniper that locks on with a laser before firing a fast purple beam."""
    SPRITE_PATH = "patchouli.png"
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 3
    SPEED = 1
    FIRE_COOLDOWN = 3000
    FIRE_SPEED = 400
    FIRE_COLOR = (128, 0, 128)          # purple beam
    FIRE_ON_SCREEN_ONLY = True          # won't fire off-screen
    IS_SNIPER = True                    # enables laser + lock-on
    SNIPER_WARN_TIME = 500              # ms of red warning before shot
    SNIPER_LASER_TRACK_COLOR = (200, 100, 255)  # tracking laser color
    SNIPER_LASER_WARN_COLOR = (255, 50, 50)     # lock-on warning color
