import random
from director.enemy_currency_weight import ENEMY_COST, ENEMY_UNLOCK_WAVE, ENEMY_BASE_WEIGHT

class WaveDirector:
    def __init__(self, spawn_enemy_callback, active_enemies_ref):
        """
        :param spawn_enemy_callback: Function to call when spawning an enemy. i.e., `spawn_enemy(enemy_type)`
        :param active_enemies_ref: Reference to the collection (list/set/Group) of active enemies
        """
        self.spawn_enemy = spawn_enemy_callback
        self.active_enemies = active_enemies_ref
        
        self.current_wave = 0
        self.difficulty = 0.0
        self.spawn_queue = []
        
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0
        
    def generate_wave(self):
        """Advances wave, computes budget based on difficulty, and fills spawn queue."""
        self.current_wave += 1
        
        # 1. Scale difficulty and determine budget
        self.difficulty = self.current_wave * 1.5
        budget = 20 + int(self.difficulty * 10)
        
        # 2. Build allowed pool based on unlock wave limits
        available_enemies = [
            e_type for e_type, unlock_wave in ENEMY_UNLOCK_WAVE.items()
            if unlock_wave <= self.current_wave
        ]
        
        if not available_enemies:
            available_enemies = ["grunt"]

        # 3. Dynamically adjust weights over time to evolve challenge 
        dynamic_weights = {}
        for e_type in available_enemies:
            base_w = ENEMY_BASE_WEIGHT.get(e_type, 10)
            if e_type == "grunt":
                # Reduce grunt spammability in extremely late waves
                dynamic_weights[e_type] = max(10, base_w - self.current_wave * 2)
            else:
                # Slightly increase likelihood of higher tier enemies as we progress
                dynamic_weights[e_type] = base_w + self.current_wave * 1
                
        # 4. Process budget to populate the queue
        min_cost = min((ENEMY_COST.get(e, 1) for e in available_enemies), default=1)
        
        while budget >= min_cost:
            # Filter enemies we can actually afford with remaining budget
            affordable_enemies = [e for e in available_enemies if ENEMY_COST.get(e, 1) <= budget]
            if not affordable_enemies:
                break
                
            chosen_type = self._weighted_random_choice(affordable_enemies, dynamic_weights)
            cost = ENEMY_COST.get(chosen_type, 1)
            
            self.spawn_queue.append(chosen_type)
            budget -= cost
            
        # Store total count to display in UI
        self.total_enemies_this_wave = len(self.spawn_queue)
            
        # Shuffle spawn queue to interleave different unit types
        random.shuffle(self.spawn_queue)
        
        # 5. Speed up spawn intervals slightly every wave for increased pressure
        self.spawn_interval = max(0.2, 1.0 - (self.current_wave * 0.02))
        self.spawn_timer = 0.0

    def _weighted_random_choice(self, available_enemies, dynamic_weights):
        """Helper to safely handle weighted selection."""
        total_weight = sum(dynamic_weights[e] for e in available_enemies)
        
        if total_weight <= 0:
            return random.choice(available_enemies)
            
        rand_val = random.uniform(0, total_weight)
        current = 0
        for e in available_enemies:
            current += dynamic_weights[e]
            if rand_val <= current:
                return e
                
        return available_enemies[-1]

    def update(self, dt):
        """Called every frame. Handles timing for releasing spawns iteratively."""
        if not self.spawn_queue:
            return
            
        self.spawn_timer += dt
        
        if self.spawn_timer >= self.spawn_interval and self.spawn_queue:
            next_enemy = self.spawn_queue.pop(0)
            self.spawn_enemy(next_enemy)
            
            self.spawn_timer -= self.spawn_interval
            
            # Bound timer to prevent recursive dumping if delta-time spikes (e.g., lag spike)
            if self.spawn_timer > self.spawn_interval * 2:
                self.spawn_timer = self.spawn_interval

    def is_wave_complete(self):
        """
        Wave evaluates to completed only when logic says NO queued spawns 
        and NO physical instances reside in the world data representation.
        """
        return len(self.spawn_queue) == 0 and len(self.active_enemies) == 0