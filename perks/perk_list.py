# perk_list.py
# all available perks live here as simple dicts
# to add a new perk: drop a png into perks/perk_png/ and add an entry below
# keys:
#   name        - display name on the card
#   description - short stat description
#   stat        - player attribute name to modify
#   delta       - how much to add to that attribute
#   icon        - path to the png (relative to project root), or None for no image

ALL_PERKS = [

    #------------------------------------------
    # offense perks / hitting harder and faster
    #------------------------------------------
    {
        "name":        "Faster Bullets",
        "description": "Bullet speed +5",
        "stat":        "bullet_speed",
        "delta":       5,
        "icon":        "perks/perk_png/faster_bullets.png",
    },
    {
        "name":        "Hair Trigger",
        "description": "Shoot cooldown -10ms",
        "stat":        "shoot_cooldown",
        "delta":       -10,
        "icon":        "perks/perk_png/hair_trigger.png",
    },
    {
        "name":        "Overclocked",
        "description": "Shoot cooldown -20ms",
        "stat":        "shoot_cooldown",
        "delta":       -20,
        "icon":        "perks/perk_png/overclocked.png",
    },

    #------------------------------------------
    # defense perks / staying alive longer
    #------------------------------------------
    {
        "name":        "Extra HP",
        "description": "Max HP +1",
        "stat":        "max_hp",
        "delta":       1,
        "icon":        "perks/perk_png/extra_hp.png",
    },
    {
        "name":        "Quick Dash",
        "description": "Dash cooldown -100ms",
        "stat":        "dash_cooldown",
        "delta":       -100,
        "icon":        "perks/perk_png/quick_dash.png",
    },
    {
        "name":        "Longer Dash",
        "description": "Dash duration +50ms",
        "stat":        "dash_duration",
        "delta":       50,
        "icon":        "perks/perk_png/longer_dash.png",
    },

    #------------------------------------------
    # mobility perks / getting around faster
    #------------------------------------------
    {
        "name":        "Afterburner",
        "description": "Dash speed multiplier +0.5",
        "stat":        "dash_speed_multiplier",
        "delta":       0.5,
        "icon":        "perks/perk_png/afterburner.png",
    },

]
