import numpy as np

class ProjectileManager:
    """
    Data-Oriented Projectile Manager.
    Instead of thousands of Python objects, we use parallel 1D numpy arrays.
    """
    def __init__(self, max_bullets=20000):
        self.max_bullets = max_bullets
        self.active_count = 0
        
        # We need these attributes for the shader:
        # pos(2f), color(3f), radius(1f), angle(1f), type(1i) => 8 floats
        # But we also need dir/velocity for updates.
        
        # Parallel Arrays
        self.active = np.zeros(max_bullets, dtype=bool)
        
        # Geometry / Physics
        self.pos_x = np.zeros(max_bullets, dtype=np.float32)
        self.pos_y = np.zeros(max_bullets, dtype=np.float32)
        self.vel_x = np.zeros(max_bullets, dtype=np.float32)
        self.vel_y = np.zeros(max_bullets, dtype=np.float32)
        self.radius = np.zeros(max_bullets, dtype=np.float32)
        self.angle = np.zeros(max_bullets, dtype=np.float32)
        
        # Aesthetics
        self.color_r = np.zeros(max_bullets, dtype=np.float32)
        self.color_g = np.zeros(max_bullets, dtype=np.float32)
        self.color_b = np.zeros(max_bullets, dtype=np.float32)
        self.type_id = np.zeros(max_bullets, dtype=np.float32) # float32 for easy struct packing later
        
        # Ownership (0 = player, 1 = enemy)
        self.owner = np.zeros(max_bullets, dtype=np.int32)
        
        # Output buffer specifically tailored to matches the VBO layout
        # (pos_x, pos_y, r, g, b, radius, angle, type_id)
        self.vbo_data = np.zeros((max_bullets, 8), dtype=np.float32)

    def spawn(self, x, y, dx, dy, speed, radius, color, type_id, owner, angle=0.0):
        """Finds the first inactive slot and spawns a bullet."""
        if self.active_count >= self.max_bullets:
            return # Pool is full
            
        # Very fast way to find the first False in boolean array
        idx = np.argmin(self.active)
        
        self.active[idx] = True
        self.pos_x[idx] = x
        self.pos_y[idx] = y
        self.vel_x[idx] = dx * speed
        self.vel_y[idx] = dy * speed
        self.radius[idx] = radius
        self.angle[idx] = angle
        self.color_r[idx] = color[0] / 255.0
        self.color_g[idx] = color[1] / 255.0
        self.color_b[idx] = color[2] / 255.0
        self.type_id[idx] = type_id
        self.owner[idx] = owner
        
        self.active_count += 1

    def update(self, map_w, map_h):
        """Vectorized update of all active bullets."""
        if self.active_count == 0:
            return
            
        # Only update active bullets
        # np.where(self.active) gives the indices of active elements, but boolean indexing is also very fast
        
        # 1. Update positions
        self.pos_x[self.active] += self.vel_x[self.active]
        self.pos_y[self.active] += self.vel_y[self.active]
        
        # 2. Map Boundaries Check
        # Disable objects out of bounds
        out_of_bounds = (
            (self.pos_x < 0) | (self.pos_x > map_w) |
            (self.pos_y < 0) | (self.pos_y > map_h)
        )
        
        # We only want to turn True active elements to False
        to_deactivate = self.active & out_of_bounds
        
        if np.any(to_deactivate):
            self.active[to_deactivate] = False
            self.active_count = np.count_nonzero(self.active)

    def get_vbo_data(self):
        """Returns contiguous numpy data containing exactly what the GPU expects."""
        if self.active_count == 0:
            return np.array([], dtype=np.float32)
            
        # Select active boolean masks
        act = self.active
        
        # Construct the (N, 8) layout. We can use np.vstack or column_stack.
        # But even faster is to map it directly into a pre-allocated array.
        
        # 0: pos_x, 1: pos_y, 2: r, 3: g, 4: b, 5: radius, 6: angle, 7: type_id
        # Note: In Python, indexing subsets using `act` makes a copy anyway, but it's very fast in C.
        result = np.column_stack((
            self.pos_x[act],
            self.pos_y[act],
            self.color_r[act],
            self.color_g[act],
            self.color_b[act],
            self.radius[act],
            self.angle[act],
            self.type_id[act]
        ))
        
        return result.astype(np.float32)
