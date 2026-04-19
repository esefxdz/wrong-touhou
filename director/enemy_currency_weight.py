# Maps enemy type to integer cost (used for budget-based spawning)
ENEMY_COST = {
    "rumia": 1,
    "cirno": 3,
    "sakuya": 4,
    "patchouli": 5,
    "yukari": 8,
    "tewi": 4,
    "sanae": 5,
    "flandre": 6
}

# Maps enemy type to the wave number when it becomes available
ENEMY_UNLOCK_WAVE = {
    "rumia": 1,
    "cirno": 3,
    "sakuya": 4,
    "patchouli": 5,
    "yukari": 6,
    "tewi": 4,
    "sanae": 5,
    "flandre": 6
}

# Base spawn weight for each enemy (used in weighted random selection)
ENEMY_BASE_WEIGHT = {
    "rumia": 70,
    "cirno": 20,
    "sakuya": 15,
    "patchouli": 10,
    "yukari": 3,
    "tewi": 15,
    "sanae": 10,
    "flandre": 8
}