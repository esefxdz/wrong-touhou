from baddies.rumia import Rumia
from baddies.cirno import Cirno
from baddies.patchouli import Patchouli

ENEMY_REGISTRY = {
    "rumia": Rumia,
    "cirno": Cirno,
    "patchouli": Patchouli,
}

def spawn_enemy(name, player_ref):
    """Spawn an enemy by name. Returns the enemy instance."""
    enemy_class = ENEMY_REGISTRY.get(name)
    if enemy_class is None:
        raise ValueError(f"Unknown enemy type: {name}")
    return enemy_class(player_ref)
