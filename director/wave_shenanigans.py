import pygame

class WaveTransitionTimer:
    def __init__(self, delay_ms=3000):
        # basic timer settings
        self.delay_ms = delay_ms
        self.waiting = False
        self.wait_start_time = 0
        
    def check_transition(self, is_complete, current_time, shop_menu):
        # wait if wave is finished but we haven't opened shop yet
        if is_complete:
            if not self.waiting and not shop_menu.active:
                self.waiting = True
                self.wait_start_time = current_time
                
            # check the delay
            if self.waiting and not shop_menu.active:
                elapsed = current_time - self.wait_start_time
                if elapsed >= self.delay_ms:
                    # boom shop time
                    shop_menu.trigger()
                    self.waiting = False
        else:
            # resets when new wave kicks in
            self.waiting = False
