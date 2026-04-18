from baddies.base_enemy import BaseEnemy

class Sakuya(BaseEnemy):
    """Sakuya - Spinner enemy with orbiting blades that tries to physically hit you."""
    SPRITE_PATH = "sakuya.png"
    SPRITE_SIZE = (150, 150)
    HITBOX_SIZE = (50, 50)
    MAX_HP = 5              # Tougher
    SPEED = 2.0             # Fast pursuit
    
    FIRE_COUNT = 0          # She doesn't shoot standard bullets
    
    # Spinner configuration
    IS_SPINNER = True
    SPINNER_BLADE_COUNT = 2
    SPINNER_RADIUS = 90     # Orbit distance
    SPINNER_SPEED = 0.08    # Spin speed
    SPINNER_COLOR = (192, 192, 192) # Silver knives/blades
    SPINNER_BLADE_RADIUS = 15 # Threat size