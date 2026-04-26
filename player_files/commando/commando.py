from player_files.base_player import BasePlayer

class Commando(BasePlayer):
    """Commando - balanced starter character."""

    NAME        = "Commando"
    DESCRIPTION = "A well-rounded soldier. Fast shooter, sturdy health."
    PORTRAIT_PATH = "commando/commando_sprite.png"  # reuse first frame as portrait

    SPRITE_PATH  = "commando/commando_sprite.png"
    SPRITE_SIZE  = (64, 64)
    FRAME_COUNT  = 8           # adjust to the actual number of frames in your sheet
    FRAME_SPEED  = 100         # ms per frame

    HITBOX_SIZE    = (50, 50)
    MAX_HP         = 6
    PLAYER_SPEED   = 10
    BULLET_SPEED   = 28
    SHOOT_COOLDOWN = 65

    HITBOX_RADIUS = 6
    GRAZE_RADIUS  = 28

    JUMP_STRENGTH   = -12.0
    DASH_COOLDOWN   = 900
    DASH_DURATION   = 200
    DASH_MULTIPLIER = 3.5
