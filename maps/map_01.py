# Map 01 - Default Map
import os

MAP_NAME = "The Field"
MAP_IMAGE = os.path.join("maps", "map_01.jpg")
MAP_WIDTH = 3000
MAP_HEIGHT = 3000

GRAVITY = 0.5
COLLISION_RECTS = [
    (0, 2750, 3000, 250)
]

#DOESNT WORK
# enemy spawning
ENEMY_WAVES = [
    {"enemy": "rumia", "interval": 2000, "count": 3},
    {"enemy": "cirno", "interval": 1500, "count": 5},
    {"enemy": "patchouli", "interval": 1500, "count": 5}
]

#DOESNT WORK
# enemy types available on this map
ENEMY_TYPES = ["rumia", "cirno", "patchouli"]
