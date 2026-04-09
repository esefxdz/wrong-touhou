# Enemy registry - maps reference enemies by name string
from baddies.rumia import Rumia

ENEMY_REGISTRY = {
    "rumia": Rumia,
    # add new enemies here:
    # "cirno": Cirno,
    # "sakuya": Sakuya,
}

def spawn_enemy(name, player_ref):
    """Spawn an enemy by name. Returns the enemy instance."""
    enemy_class = ENEMY_REGISTRY.get(name)
    if enemy_class is None:
        raise ValueError(f"Unknown enemy type: {name}")
    return enemy_class(player_ref)
