import random
from director.enemy_currency_weight import ENEMY_COST, ENEMY_UNLOCK_WAVE, ENEMY_BASE_WEIGHT

class WaveDirector:

    #------------------------------------------
    # initialization / hooking up spawn callback and map
    # target: @everyone
    #------------------------------------------
    def __init__(self, spawn_enemy_callback, active_enemies_ref, current_map=None):
        self.spawn_enemy = spawn_enemy_callback
        self.active_enemies = active_enemies_ref
        self.current_map = current_map
        
        self.current_wave = 0
        self.difficulty = 0.0
        self.spawn_queue = []
        
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0

    #------------------------------------------
    # wave generation / budget-based enemy queue
    # target: @everyone
    #------------------------------------------
    def generate_wave(self):
        self.current_wave += 1
        
        # scale difficulty and determine budget
        self.difficulty = self.current_wave * 1.5
        budget = 20 + int(self.difficulty * 10)
        
        # build allowed pool based on unlock wave
        available_enemies = [
            e_type for e_type, unlock_wave in ENEMY_UNLOCK_WAVE.items()
            if unlock_wave <= self.current_wave
        ]
        
        # filter by map's ENEMY_TYPES if the map defines one
        if self.current_map and self.current_map.ENEMY_TYPES:
            available_enemies = [e for e in available_enemies if e in self.current_map.ENEMY_TYPES]

        if not available_enemies:
            available_enemies = ["grunt"]

        # adjust weights over time
        dynamic_weights = {}
        for e_type in available_enemies:
            base_w = ENEMY_BASE_WEIGHT.get(e_type, 10)
            if e_type == "grunt":
                dynamic_weights[e_type] = max(10, base_w - self.current_wave * 2)
            else:
                dynamic_weights[e_type] = base_w + self.current_wave * 1

        # fill queue from budget
        min_cost = min((ENEMY_COST.get(e, 1) for e in available_enemies), default=1)
        while budget >= min_cost:
            affordable_enemies = [e for e in available_enemies if ENEMY_COST.get(e, 1) <= budget]
            if not affordable_enemies:
                break
            chosen_type = self._weighted_pick(affordable_enemies, dynamic_weights)
            self.spawn_queue.append(chosen_type)
            budget -= ENEMY_COST.get(chosen_type, 1)

        self.total_enemies_this_wave = len(self.spawn_queue)
        random.shuffle(self.spawn_queue)
        
        # speed up spawns slightly each wave
        self.spawn_interval = max(0.2, 1.0 - (self.current_wave * 0.02))
        self.spawn_timer = 0.0

    #------------------------------------------
    # weighted random helper / used in generate_wave
    # target: @everyone
    #------------------------------------------
    def _weighted_pick(self, available_enemies, dynamic_weights):
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

    #------------------------------------------
    # update / drip-feeds the queue each frame
    # target: @everyone
    #------------------------------------------
    def update(self, dt):
        if not self.spawn_queue:
            return
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and self.spawn_queue:
            self.spawn_enemy(self.spawn_queue.pop(0))
            self.spawn_timer -= self.spawn_interval
            if self.spawn_timer > self.spawn_interval * 2:
                self.spawn_timer = self.spawn_interval

    #------------------------------------------
    # wave completion check / no queue and no living enemies
    # target: @everyone
    #------------------------------------------
    def is_wave_complete(self):
        return len(self.spawn_queue) == 0 and len(self.active_enemies) == 0