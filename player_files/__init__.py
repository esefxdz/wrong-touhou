from player_files.commando.commando import Commando

PLAYER_REGISTRY = {
    "commando": Commando,
}

def create_player(name, x, y, map_w, map_h):
    """Spawn a player by registry name."""
    cls = PLAYER_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown player type: {name}")
    return cls(x, y, map_w, map_h)
