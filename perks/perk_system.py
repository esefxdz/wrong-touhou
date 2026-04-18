# perk_system.py
# handles applying a chosen perk to the player
# keep this separate so perk logic doesnt bleed into level.py or player.py

import random
from perks.perk_list import ALL_PERKS

#------------------------------------------
# perk application / changing the player stat
#------------------------------------------
def apply_perk(player, perk):
    """Takes a perk dict and applies its delta to the matching player attribute."""
    stat = perk["stat"]
    delta = perk["delta"]
    if hasattr(player, stat):
        current = getattr(player, stat)
        setattr(player, stat, current + delta)

#------------------------------------------
# perk selection / picking a random set of choices
#------------------------------------------
def get_perk_choices(count=3):
    """Returns a list of 'count' randomly chosen perks from ALL_PERKS."""
    pool = list(ALL_PERKS)
    random.shuffle(pool)
    return pool[:count]
