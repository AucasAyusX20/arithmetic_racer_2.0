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
GRID_COLOR = (0, 255, 255)    
HORIZON_LINE = (255, 0, 128)  
ROAD_GREY = (15, 15, 20)      
ROAD_LINE_WHITE = (255, 255, 255)

# Gradient Sun
SUN_TOP_COLOR = (255, 255, 0)   # bright yellow crown
SUN_BASE_COLOR = (255, 0, 128)  # deep neon pink at the horizon

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

# --- SUN GEOMETRY ---
SUN_RADIUS = 100      # disc radius, unchanged from the original sun
SUN_HALO_PAD = 20     # margin kept above the disc for the outer glow ring

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
        self.name_input = ""
        self.scroll_offset = 0.0
        self.sun_canvas = None
        
        self.stars = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HORIZON_Y - 100), 
                        "scale": random.uniform(0.5, 1.5)} for _ in range(60)]
        
        self.skyline = []
        x = 0
        while x < WIDTH:
            w = random.randint(20, 50)
            h = random.randint(10, 80)
            
            # Pre-generate windows so they don't flicker every frame
            windows = []
            for wx in range(x + 5, x + w - 5, 8):
                for wy in range(HORIZON_Y - h + 5, HORIZON_Y - 5, 10):
                    if random.random() > 0.7:
                        windows.append((wx, wy, random.choice([(0, 255, 255), (255, 0, 128), (255, 255, 0)])))
            
            self.skyline.append({"x": x, "w": w, "h": h, "windows": windows})
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

    # --- VISUAL HELPERS (rendering only — no game logic touched) ---

    def lerp_color(self, c1, c2, t):
        """Blend two RGB colors: t = 0 returns c1, t = 1 returns c2."""
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

    def neon_line(self, color, start, end, width=4):
        """Draw a line with a cheap layered neon glow: wide dim halo layers
        stack down to a bright, crisp core (no per-frame alpha surfaces)."""
        for grow, glow in ((14, 0.16), (9, 0.32), (5, 0.55), (0, 1.0)):
            faded = tuple(int(c * glow) for c in color)
            pygame.draw.line(screen, faded, start, end, max(1, width + grow))

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

        for b in self.skyline:
            # Draw the building base
            pygame.draw.rect(screen, (15, 10, 25), (b["x"], HORIZON_Y - b["h"], b["w"], b["h"]))
            # Draw the neon outline
            pygame.draw.rect(screen, (255, 0, 128), (b["x"], HORIZON_Y - b["h"], b["w"], b["h"]), 1)
            # Draw the pre-generated windows
            for wx, wy, color in b["windows"]:
                pygame.draw.rect(screen, color, (wx, wy, 4, 6))

        # --- SYNTHWAVE GRADIENT SUN ---
        # The sun sprite never changes frame-to-frame, so its scanline loops
        # run exactly once in build_sun_canvas(); every frame we just blit it.
        if self.sun_canvas is None:
            self.sun_canvas = self.build_sun_canvas()
        sun_x = WIDTH//2 - SUN_RADIUS - SUN_HALO_PAD
        sun_y = HORIZON_Y - SUN_RADIUS - SUN_HALO_PAD
        screen.blit(self.sun_canvas, (sun_x, sun_y))

        pygame.draw.line(screen, HORIZON_LINE, (0, HORIZON_Y), (WIDTH, HORIZON_Y), 4)

    def build_sun_canvas(self):
        """Renders the gradient sun once into a reusable canvas:
        1) scanline gradient fill — bright yellow crown fading to deep
           neon pink at the horizon, clipped to the disc's curve,
        2) retro SKY_BOTTOM stripe cutouts, per-scanline so they end crisply
           on the sun's silhouette,
        3) a subtle glowing rim, stroked in vertical bands (yellow to pink)
           with per-pixel alpha halos fading into a crisp core edge."""
        sun_radius = SUN_RADIUS
        pad = SUN_HALO_PAD
        canvas_w = (sun_radius + pad) * 2
        canvas_h = sun_radius + pad + 2
        canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
        cx = canvas_w // 2
        base_y = pad + sun_radius   # circle center maps to the horizon row
        sun_top = base_y - sun_radius

        # 1) Scanline gradient fill: one horizontal line per row.
        for y in range(sun_top, base_y + 1):
            t = (y - sun_top) / sun_radius
            color = self.lerp_color(SUN_TOP_COLOR, SUN_BASE_COLOR, t)
            dy = base_y - y
            half_w = int((sun_radius * sun_radius - dy * dy) ** 0.5 + 0.5)
            if half_w > 0:
                pygame.draw.line(canvas, color, (cx - half_w, y), (cx + half_w, y))

        # 2) Retro stripe cutouts. Each row is clipped to the disc as it is
        #    drawn, so the stripes end cleanly on the silhouette. The first
        #    stripe starts below the crown to keep the yellow cap solid.
        stripe_h = 7
        for i in range(6):
            stripe_y = sun_top + 14 + (i * 18)
            if stripe_y >= base_y: break
            for y in range(stripe_y, min(stripe_y + stripe_h, base_y)):
                dy = base_y - y
                half_w = int((sun_radius * sun_radius - dy * dy) ** 0.5 + 0.5)
                if half_w > 0:
                    pygame.draw.line(canvas, SKY_BOTTOM, (cx - half_w, y), (cx + half_w, y))

        # 3) Subtle glowing outline. Rings are written with per-pixel alpha
        #    (wide, faint halo down to a crisp colored core) so the cached
        #    canvas glows softly over the sky and skyline when blitted.
        rim_layers = ((18, 4, 12), (15, 3, 18), (12, 3, 26), (9, 3, 36),
                      (6, 3, 52), (4, 3, 76), (2, 2, 120), (1, 2, 255))
        bands = 24
        step = (sun_radius + pad) / float(bands)
        for b in range(bands):
            top = int(sun_top - pad + b * step)
            bottom = int(top + step + 2)
            if bottom <= top: continue
            band_h = bottom - top
            y_mid = top + band_h * 0.5
            t_mid = max(0.0, min(1.0, (y_mid - sun_top) / float(sun_radius)))
            rim_color = self.lerp_color(SUN_TOP_COLOR, SUN_BASE_COLOR, t_mid)
            canvas.set_clip((0, top, canvas_w, band_h))
            for grow, width, alpha in rim_layers:
                pygame.draw.circle(canvas, (*rim_color, alpha), (cx, base_y), sun_radius + grow, width)
            canvas.set_clip(None)
        return canvas.convert_alpha()


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

        # Thick glowing cyan shoulders + neon pink center line.
        self.neon_line(GRID_COLOR, road_points[0], road_points[3], 6)
        self.neon_line(GRID_COLOR, road_points[1], road_points[2], 6)
        self.neon_line(HORIZON_LINE, (WIDTH//2, HORIZON_Y), (WIDTH//2, HEIGHT), 6)

        # Dashed white lane dividers at 1/3 and 2/3 of the road width.
        # z*0.15 spans the whole scroll period (the old range(20) only
        # reached 5.7, so the dashes blinked out of existence every cycle).
        for z in range(76):
            depth = ((z * 0.15) - (self.scroll_offset % 10000) / 1000.0)
            if 0 < depth < 1.0:
                p = depth ** 2.5
                # Measure the dash in depth space so the on-screen dash/gap
                # rhythm stays consistent instead of stretching near the bike.
                p_end = min(1.0, depth + 0.075) ** 2.5
                y1 = HORIZON_Y + p * (HEIGHT - HORIZON_Y)
                y2 = HORIZON_Y + p_end * (HEIGHT - HORIZON_Y)

                if y1 < HEIGHT:
                    width = max(4, int(4 + p * 10))
                    for i in (1, 2):
                        top_x = (WIDTH//2 - ROAD_WIDTH_TOP//2) + (ROAD_WIDTH_TOP * (i/3))
                        bot_x = (WIDTH//2 - ROAD_WIDTH_BOTTOM//2) + (ROAD_WIDTH_BOTTOM * (i/3))
                        x1 = top_x + p * (bot_x - top_x)
                        x2 = top_x + p_end * (bot_x - top_x)
                        pygame.draw.line(screen, ROAD_LINE_WHITE, (x1, y1), (x2, y2), width)

    def draw_forest(self):
        sorted_trees = sorted(self.trees, key=lambda t: t["z"])

        for t in sorted_trees:
            p = t["z"] ** 2.5

            # Size is computed first so placement can use the canopy width.
            th = 220 * p * t["scale"]
            tw = 70 * p * t["scale"]
            if th < 3: continue

            current_road_width = ROAD_WIDTH_TOP + p * (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP)
            half_road = current_road_width * 0.5
            road_edge = WIDTH * 0.5 + t["side"] * half_road
            space_available = WIDTH * 0.5 - half_road

            # Reserve a clear shoulder between the glowing road border and
            # the nearest canopy, then distribute the tree in the space left.
            tree_half = tw * 0.5
            shoulder = 12 + p * 30
            setback = tree_half + shoulder
            spread = max(0.0, space_available - setback - tree_half - 4)
            tx = road_edge + t["side"] * (setback + t["x_offset"] * spread)

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
                # Shading gradient for a 3D look:
                # i == 0 (bottom layer): darken by 30
                # i == 1 (middle layer): base color
                # i == 2 (top layer): brighten by 30
                shade = -30 if i == 0 else (30 if i == 2 else 0)
                shaded_color = tuple(max(0, min(255, c + shade)) for c in t["color"])
                pygame.draw.polygon(screen, shaded_color, points)

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