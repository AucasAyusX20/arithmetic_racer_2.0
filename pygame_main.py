# pygame_main.py
import pygame
import sys
import random
from game_state import GameState

# --- INITIALIZATION ---
pygame.init()
WIDTH, HEIGHT = 1280, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arithmetic Racer 2.0 - Wide Forest")

clock = pygame.time.Clock()

# --- COLORS ---
SKY_TOP = (20, 5, 25)         
SKY_BOTTOM = (60, 10, 50)     
SUN_COLOR = (255, 100, 0)     
GRID_COLOR = (0, 255, 255)    
HORIZON_LINE = (255, 0, 128)  
ROAD_GREY = (15, 15, 20)      
ROAD_LINE_WHITE = (255, 255, 255)

# Tree Colors
TRUNK_COLOR = (20, 10, 15)
LEAF_DARK = (10, 50, 30)      
LEAF_NEON = (0, 200, 100)     
LEAF_PINK = (220, 0, 120)     
FOREST_FLOOR = (5, 15, 10)    

# --- PERSPECTIVE CONSTANTS ---
HORIZON_Y = 250                   
PLAYER_Y = HEIGHT - 100           
ROAD_WIDTH_TOP = 150              
ROAD_WIDTH_BOTTOM = 800  

# --- LOAD THE BIKE IMAGE ---
try:
    BIKE_IMG = pygame.image.load("bike.png").convert_alpha()
    BIKE_IMG = pygame.transform.scale(BIKE_IMG, (140, 140)) 
except FileNotFoundError:
    print("ERROR: bike.png not found!")
    sys.exit()

class PygameRacer:
    def __init__(self):
        self.state = None
        self.app_state = "START"
        self.name_input = "AYUSH"
        self.scroll_offset = 0.0
        
        self.stars = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HORIZON_Y - 100), 
                        "scale": random.uniform(0.5, 1.5)} for _ in range(60)]
        
        self.skyline = []
        x = 0
        while x < WIDTH:
            w = random.randint(20, 50)
            h = random.randint(10, 80)
            self.skyline.append((x, w, h))
            x += w

        self.trees = []
        for _ in range(1500): 
            self.trees.append(self.create_tree(random.uniform(0.01, 1.0)))

    def create_tree(self, z_depth):
        side = random.choice([-1, 1]) 
        tree_type = random.choice(["dark", "dark", "neon", "pink"]) 
        
        if tree_type == "dark": color = LEAF_DARK
        elif tree_type == "neon": color = LEAF_NEON
        else: color = LEAF_PINK

        return {
            "side": side,
            "z": z_depth,
            "x_offset": random.uniform(0.0, 1.0), 
            "scale": random.uniform(0.8, 1.4), # Tighter scale range
            "color": color
        }

    def start_game(self):
        self.state = GameState(self.name_input)
        self.app_state = "PLAYING"

    def update(self, dt):
        dt = min(dt, 0.05)
        
        speed = 100 if self.state is None else (self.state.tier_idx * 100 + 200) * self.state.speed_multiplier
        self.scroll_offset += speed * dt

        for s in self.stars:
            s["x"] -= speed * dt * 0.02
            if s["x"] < -10: s["x"] = WIDTH + 10

        for t in self.trees:
            t["z"] += speed * dt * 0.0015 
            if t["z"] > 1.0:
                t.update(self.create_tree(0.01))

        if self.app_state == "PLAYING" and not self.state.game_over and not self.state.paused:
            self.state.update(dt)

    def draw(self):
        self.draw_sky_and_sun()
        self.draw_grid()
        self.draw_forest_floor() 
        self.draw_road()         
        self.draw_forest()       
        
        if self.app_state == "PLAYING":
            self.draw_answers()
            self.draw_player()
            self.draw_hud()
            if self.state.game_over:
                self.draw_game_over()
            elif self.state.paused:
                self.draw_pause()
        else:
            self.draw_start_screen()

    def draw_sky_and_sun(self):
        for y in range(HORIZON_Y):
            t = y / HORIZON_Y
            r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
            g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
            b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

        for s in self.stars:
            pygame.draw.circle(screen, (255, 255, 255), (int(s["x"]), int(s["y"])), max(1, int(s["scale"])))

        for (x, w, h) in self.skyline:
            pygame.draw.rect(screen, (10, 5, 15), (x, HORIZON_Y - h, w, h))
            for wx in range(x + 5, x + w - 5, 8):
                for wy in range(HORIZON_Y - h + 5, HORIZON_Y - 5, 10):
                    if random.random() > 0.7:
                        pygame.draw.rect(screen, (255, 200, 0), (wx, wy, 2, 2))

        sun_radius = 100
        pygame.draw.circle(screen, SUN_COLOR, (WIDTH//2, HORIZON_Y), sun_radius)
        for i in range(6):
            stripe_y = HORIZON_Y - sun_radius + (i * 20)
            if stripe_y < HORIZON_Y:
                pygame.draw.rect(screen, SKY_BOTTOM, (WIDTH//2 - sun_radius, stripe_y, sun_radius*2, 8))

        pygame.draw.line(screen, HORIZON_LINE, (0, HORIZON_Y), (WIDTH, HORIZON_Y), 4)

    def draw_grid(self):
        pygame.draw.rect(screen, (10, 10, 15), (0, HORIZON_Y, WIDTH, HEIGHT - HORIZON_Y))
        
        for z in range(30):
            depth = ((z * 0.4) - (self.scroll_offset % 10000) / 1000.0)
            if 0 < depth < 1.0:
                p = depth ** 2.5 
                y_pos = HORIZON_Y + p * (HEIGHT - HORIZON_Y)
                pygame.draw.line(screen, GRID_COLOR, (0, y_pos), (WIDTH, y_pos), 1)

        for i in range(-15, 16):
            start_x = WIDTH//2 + (i * 120)
            end_x = WIDTH//2 + (i * 20)
            pygame.draw.line(screen, GRID_COLOR, (start_x, HEIGHT), (end_x, HORIZON_Y), 1)

    def draw_forest_floor(self):
        left_floor = [
            (0, HEIGHT), (WIDTH//2 - ROAD_WIDTH_BOTTOM//2, HEIGHT),
            (WIDTH//2 - ROAD_WIDTH_TOP//2, HORIZON_Y), (0, HORIZON_Y)
        ]
        right_floor = [
            (WIDTH, HEIGHT), (WIDTH//2 + ROAD_WIDTH_BOTTOM//2, HEIGHT),
            (WIDTH//2 + ROAD_WIDTH_TOP//2, HORIZON_Y), (WIDTH, HORIZON_Y)
        ]
        pygame.draw.polygon(screen, FOREST_FLOOR, left_floor)
        pygame.draw.polygon(screen, FOREST_FLOOR, right_floor)

    def draw_road(self):
        road_points = [
            (WIDTH//2 - ROAD_WIDTH_TOP//2, HORIZON_Y),
            (WIDTH//2 + ROAD_WIDTH_TOP//2, HORIZON_Y),
            (WIDTH//2 + ROAD_WIDTH_BOTTOM//2, HEIGHT),
            (WIDTH//2 - ROAD_WIDTH_BOTTOM//2, HEIGHT)
        ]
        pygame.draw.polygon(screen, ROAD_GREY, road_points)

        pygame.draw.line(screen, GRID_COLOR, road_points[0], road_points[3], 5)
        pygame.draw.line(screen, GRID_COLOR, road_points[1], road_points[2], 5)
        pygame.draw.line(screen, HORIZON_LINE, (WIDTH//2, HORIZON_Y), (WIDTH//2, HEIGHT), 5)

        for z in range(20):
            depth = ((z * 0.3) - (self.scroll_offset % 10000) / 1000.0)
            if 0 < depth < 1.0:
                p = depth ** 2.5 
                y1 = HORIZON_Y + p * (HEIGHT - HORIZON_Y)
                y2 = HORIZON_Y + (p + 0.04) * (HEIGHT - HORIZON_Y)
                
                if y1 < HEIGHT:
                    width = max(1, int(p * 10))
                    for i in [1, 2]:
                        top_x = (WIDTH//2 - ROAD_WIDTH_TOP//2) + (ROAD_WIDTH_TOP * (i/3))
                        bot_x = (WIDTH//2 - ROAD_WIDTH_BOTTOM//2) + (ROAD_WIDTH_BOTTOM * (i/3))
                        current_x = top_x + p * (bot_x - top_x)
                        pygame.draw.line(screen, ROAD_LINE_WHITE, (current_x, y1), (current_x, y2), width)

    def draw_forest(self):
        sorted_trees = sorted(self.trees, key=lambda t: t["z"])
        
        for t in sorted_trees:
            p = t["z"] ** 2.5
            
            current_road_width = ROAD_WIDTH_TOP + p * (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP)
            road_edge = WIDTH//2 + t["side"] * (current_road_width // 2)
            
            space_available = (WIDTH//2) - (current_road_width // 2)
            offset = t["x_offset"] * space_available
            tx = road_edge + t["side"] * offset
            
            # --- LOWERED TREES ---
            # Reduced max height from 500 to 220, and width from 150 to 70
            th = 220 * p * t["scale"] 
            tw = 70 * p * t["scale"]  
            
            if th < 3: continue
            
            ty = HORIZON_Y + p * (HEIGHT - HORIZON_Y)
            
            trunk_rect = pygame.Rect(tx - tw*0.15, ty - th*0.2, tw*0.3, th*0.2)
            pygame.draw.rect(screen, TRUNK_COLOR, trunk_rect)
            
            for i in range(3):
                layer_w = tw * (1.0 - i*0.25)
                layer_h = th * 0.4
                layer_y = ty - th*0.2 - (i * th*0.25)
                
                points = [
                    (tx, layer_y - layer_h), 
                    (tx - layer_w/2, layer_y), 
                    (tx + layer_w/2, layer_y)  
                ]
                pygame.draw.polygon(screen, t["color"], points)

    def draw_player(self):
        lane_width_bottom = ROAD_WIDTH_BOTTOM / 3
        left_edge = WIDTH//2 - ROAD_WIDTH_BOTTOM//2
        px = int(left_edge + (self.state.current_lane + 0.5) * lane_width_bottom)
        
        shadow_surf = pygame.Surface((100, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 180), (0, 0, 100, 40))
        screen.blit(shadow_surf, (px - 50, PLAYER_Y + 15))

        bike_rect = BIKE_IMG.get_rect()
        bike_rect.centerx = px
        bike_rect.bottom = PLAYER_Y + 40 
        screen.blit(BIKE_IMG, bike_rect)

        name_surf = pygame.font.SysFont("consolas", 22, bold=True).render(self.state.name, True, (255, 255, 255))
        badge_rect = name_surf.get_rect(center=(px, bike_rect.top - 35))
        
        pygame.draw.rect(screen, (10, 10, 20), badge_rect.inflate(24, 12), border_radius=5)
        pygame.draw.rect(screen, GRID_COLOR, badge_rect.inflate(24, 12), 2, border_radius=5)
        screen.blit(name_surf, badge_rect)

    def draw_answers(self):
        if self.state.game_over: return
        
        progress = 1.0 - (self.state.time_left / self.state.total_time)
        p = progress ** 2.0 
        y_pos = HORIZON_Y + p * (PLAYER_Y - 50 - HORIZON_Y)
        
        scale = 0.1 + (1.2 * p)

        lane_width_bottom = ROAD_WIDTH_BOTTOM / 3
        left_edge = WIDTH//2 - ROAD_WIDTH_BOTTOM//2

        for i, opt in enumerate(self.state.options):
            top_x = (WIDTH//2 - ROAD_WIDTH_TOP//2) + (ROAD_WIDTH_TOP * ((i + 0.5)/3))
            bot_x = left_edge + (lane_width_bottom * (i + 0.5))
            cx = top_x + p * (bot_x - top_x)
            
            box_w = 120 * scale
            box_h = 60 * scale
            
            box_rect = pygame.Rect(cx - box_w//2, y_pos - box_h//2, box_w, box_h)
            
            pygame.draw.rect(screen, (15, 15, 25), box_rect, border_radius=int(5*scale))
            pygame.draw.rect(screen, GRID_COLOR, box_rect, max(1, int(3 * scale)), border_radius=int(5*scale))
            
            if scale > 0.15:
                font = pygame.font.SysFont("consolas", int(30 * scale), bold=True)
                txt_surf = font.render(str(opt), True, (255, 255, 255))
                screen.blit(txt_surf, (cx - txt_surf.get_width()//2, y_pos - txt_surf.get_height()//2))

    def draw_hud(self):
        hud_rect = pygame.Rect(WIDTH - 240, 20, 210, 450)
        s = pygame.Surface((hud_rect.width, hud_rect.height), pygame.SRCALPHA)
        s.fill((10, 10, 20, 230))
        screen.blit(s, (hud_rect.x, hud_rect.y))
        pygame.draw.rect(screen, GRID_COLOR, hud_rect, 3, border_radius=10)

        font = pygame.font.SysFont("consolas", 26, bold=True)
        font_small = pygame.font.SysFont("consolas", 18, bold=True)

        q_surf = font.render(self.state.q_text, True, (255, 255, 255))
        screen.blit(q_surf, (hud_rect.centerx - q_surf.get_width()//2, hud_rect.y + 30))

        ratio = max(0, self.state.time_left / self.state.total_time)
        bar_color = (0, 255, 0) if ratio > 0.5 else ((255, 200, 0) if ratio > 0.2 else (255, 0, 0))
        pygame.draw.rect(screen, (30, 30, 30), (hud_rect.x + 20, hud_rect.y + 80, hud_rect.width - 40, 20), border_radius=10)
        pygame.draw.rect(screen, bar_color, (hud_rect.x + 20, hud_rect.y + 80, int((hud_rect.width - 40) * ratio), 20), border_radius=10)
        
        t_surf = font_small.render(f"{self.state.time_left:.1f}s", True, bar_color)
        screen.blit(t_surf, (hud_rect.centerx - t_surf.get_width()//2, hud_rect.y + 105))

        mult = min(5.0, 1.0 + (self.state.question_num - 1) * 0.5)
        speed = self.state.tier_idx * 20 + 10
        
        stats = [
            ("SCORE", f"{self.state.score:,}", (255, 255, 100)),
            ("MULT", f"x{mult:.1f}", HORIZON_LINE),
            ("SPEED", f"{speed:.1f}", GRID_COLOR),
            ("TIER", f"{self.state.tier_idx + 1}", (255, 255, 255))
        ]
        
        for i, (label, value, color) in enumerate(stats):
            y_offset = hud_rect.y + 150 + (i * 60)
            lbl_surf = font_small.render(label, True, (150, 150, 150))
            val_surf = font.render(value, True, color)
            screen.blit(lbl_surf, (hud_rect.x + 20, y_offset))
            screen.blit(val_surf, (hud_rect.right - val_surf.get_width() - 20, y_offset - 5))

    def draw_start_screen(self):
        font_huge = pygame.font.SysFont("consolas", 60, bold=True)
        font_med = pygame.font.SysFont("consolas", 28, bold=True)
        
        title = font_huge.render("ARITHMETIC RACER", True, GRID_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        
        prompt = font_med.render("ENTER YOUR NAME:", True, (255, 255, 255))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 300))
        name_surf = font_huge.render(self.name_input + "_", True, (255, 255, 0))
        screen.blit(name_surf, (WIDTH//2 - name_surf.get_width()//2, 350))
        
        start_btn = font_med.render("[ PRESS ENTER TO START ]", True, HORIZON_LINE)
        screen.blit(start_btn, (WIDTH//2 - start_btn.get_width()//2, 500))

    def draw_pause(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        text = pygame.font.SysFont("consolas", 60, bold=True).render("PAUSED", True, GRID_COLOR)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))

    def draw_game_over(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        screen.blit(s, (0, 0))
        
        go_text = pygame.font.SysFont("consolas", 70, bold=True).render("GAME OVER", True, HORIZON_LINE)
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 150))
        
        score_text = pygame.font.SysFont("consolas", 40, bold=True).render(f"SCORE: {self.state.score:,}", True, (255, 255, 255))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        
        retry = pygame.font.SysFont("consolas", 30, bold=True).render("[R] Retry    [Q] Quit", True, GRID_COLOR)
        screen.blit(retry, (WIDTH//2 - retry.get_width()//2, HEIGHT//2 + 100))


def main():
    game = PygameRacer()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game.app_state == "START":
                    if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE]:
                        game.start_game()
                    elif event.key == pygame.K_BACKSPACE:
                        game.name_input = game.name_input[:-1]
                    else:
                        if len(game.name_input) < 10 and hasattr(event, 'unicode') and event.unicode.isalnum():
                            game.name_input += event.unicode.upper()
                else:
                    if event.key == pygame.K_p and not game.state.game_over:
                        game.state.paused = not game.state.paused
                    elif event.key == pygame.K_q:
                        running = False
                    elif event.key in [pygame.K_LEFT, pygame.K_a] and not game.state.paused and not game.state.game_over:
                        game.state.target_lane = max(0, game.state.target_lane - 1)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d] and not game.state.paused and not game.state.game_over:
                        game.state.target_lane = min(2, game.state.target_lane + 1)
                    elif event.key == pygame.K_r and game.state.game_over:
                        game.start_game()

        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()