import pygame
from constants import WHITE

class Bullet:
    """A lightweight bullet object using __slots__ for memory efficiency."""
    __slots__ = ['pos_x', 'pos_y', 'dir_x', 'dir_y', 'active', 'color', 'radius', 'type_id', 'angle']
    
    def __init__(self):
        self.active = False
        self.pos_x = 0
        self.pos_y = 0
        self.dir_x = 0
        self.dir_y = 0
        self.color = WHITE
        self.radius = 5
        self.type_id = 0 # 0 = Circle, 1 = Bullet PNG
        self.angle = 0

    def reset(self, x, y, dx, dy, color=WHITE, radius=5, type_id=0):
        """Re-initializes the bullet for reuse."""
        self.pos_x = x
        self.pos_y = y
        self.dir_x = dx
        self.dir_y = dy
        self.active = True
        self.color = color
        self.radius = radius
        self.type_id = type_id
        import math
        self.angle = math.atan2(dy, dx)

class DynamicPool:
    """A dynamic object pool that grows as needed."""
    def __init__(self, initial_size=100):
        self.inactive = [Bullet() for _ in range(initial_size)]
        self.active_count = 0

    def get(self, x, y, dx, dy, color=WHITE, radius=5, type_id=0):
        """Grabs a bullet from the pool or grows it if empty."""
        if not self.inactive:
            # Grow by 50% or at least 50 units
            growth_size = max(50, len(self.inactive) // 2)
            self.inactive.extend([Bullet() for _ in range(growth_size)])
            
        bullet = self.inactive.pop()
        bullet.reset(x, y, dx, dy, color, radius, type_id)
        self.active_count += 1
        return bullet

    def return_to_pool(self, bullet):
        """Deactivates a bullet and returns it to the pool."""
        if bullet.active:
            bullet.active = False
            self.inactive.append(bullet)
            self.active_count -= 1
