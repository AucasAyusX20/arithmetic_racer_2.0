# game_state.py
import random
from config import TIERS, get_tier_index, get_multiplier

class GameState:
    def __init__(self, player_name):
        self.name = player_name[:2].upper() if len(player_name) >= 2 else "PL"
        self.reset()

    def reset(self):
        self.score = 0
        self.question_num = 1
        self.correct_answers = 0
        self.game_over = False
        self.paused = False  # <--- CRITICAL FIX
        self.speed_multiplier = 1.0
        
        self.target_lane = 1       
        self.current_lane = 1.0    
        self.particles = []        
        self.generate_question()

    def generate_question(self):
        tier_idx = get_tier_index(self.question_num)
        tier = TIERS[tier_idx]
        
        self.tier_idx = tier_idx
        self.total_time = tier["D"] / (tier["v0"] * self.speed_multiplier)
        self.time_left = self.total_time
        
        op = random.choice(tier["ops"])
        if op == "+":
            max_val = 10 if tier_idx == 0 else (100 if tier_idx < 3 else 999)
            a, b = random.randint(1, max_val), random.randint(1, max_val)
            ans, q_str = a + b, f"{a} + {b} = ?"
        elif op == "-":
            max_val = 100 if tier_idx < 3 else 999
            a = random.randint(max_val//2, max_val)
            b = random.randint(1, max_val//2)
            ans, q_str = a - b, f"{a} - {b} = ?"
        else: 
            a = random.randint(2, 9) if tier_idx == 3 else random.randint(2, 12)
            b = random.randint(2, 9) if tier_idx == 3 else random.randint(2, 12)
            ans, q_str = a * b, f"{a} x {b} = ?"

        self.q_text = q_str
        self.correct_answer = ans
        
        self.options = [ans]
        while len(self.options) < 3:
            offset = random.choice([-20, -10, -2, -1, 1, 2, 10, 20])
            fake = ans + offset
            if fake >= 0 and fake not in self.options:
                if ans >= 20 and (fake % 10 == ans % 10):
                    continue 
                self.options.append(fake)
                
        random.shuffle(self.options)
        self.correct_lane = self.options.index(ans)

    def update(self, dt):
        if self.game_over or self.paused: return

        if self.current_lane < self.target_lane:
            self.current_lane = min(self.target_lane, self.current_lane + 5.0 * dt)
        elif self.current_lane > self.target_lane:
            self.current_lane = max(self.target_lane, self.current_lane - 5.0 * dt)
            
        self.time_left -= dt
        
        for p in self.particles:
            p['y'] -= 10 * dt
            p['life'] -= dt
        self.particles = [p for p in self.particles if p['life'] > 0]

        if self.time_left <= 0:
            self.resolve_collision()

    def resolve_collision(self):
        chosen_lane = round(self.current_lane)
        if chosen_lane == self.correct_lane:
            self.correct_answers += 1
            mult = get_multiplier(self.question_num)
            points = int(TIERS[self.tier_idx]["base_score"] * mult)
            self.score += points
            self.question_num += 1
            self.speed_multiplier = min(1.45, self.speed_multiplier + 0.06)
            self.particles.append({"text": f"+{points}", "lane": chosen_lane, "y": 17, "life": 1.0})
            self.generate_question()
        else:
            self.game_over = True