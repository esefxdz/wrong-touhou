from baddies.rumia import Rumia
from baddies.cirno import Cirno
from baddies.patchouli import Patchouli
from baddies.sakuya import Sakuya
from baddies.yukari import Yukari
from baddies.flandre import Flandre
from baddies.sanae import Sanae
from baddies.tewi import Tewi

ENEMY_REGISTRY = {
    "rumia": Rumia,
    "cirno": Cirno,
    "patchouli": Patchouli,
    "sakuya": Sakuya,
    "yukari": Yukari,
    "flandre": Flandre,
    "sanae": Sanae,
    "tewi": Tewi,
}

def spawn_enemy(name, player_ref):
    """Spawn an enemy by name. Returns the enemy instance."""
    enemy_class = ENEMY_REGISTRY.get(name)
    if enemy_class is None:
        raise ValueError(f"Unknown enemy type: {name}")
    return enemy_class(player_ref)
