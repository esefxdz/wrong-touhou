# Map 02
import os

MAP_NAME = "The Void"
MAP_IMAGE = os.path.join("maps", "map_02.jpg")
MAP_WIDTH = 4000
MAP_HEIGHT = 4000

# enemy spawning
ENEMY_WAVES = [
    {"enemy": "rumia", "interval": 1500, "count": 5},
    {"enemy": "cirno", "interval": 1500, "count": 5}
]

# enemy types available on this map
ENEMY_TYPES = ["rumia", "cirno"]
