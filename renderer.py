# renderer.py
import sys
import os
import random

# Added back so the import in main.py works perfectly
def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        sys.stdout.write('\033[H')

def draw_start_screen(name_input, scroll_offset):
    W, H = 80, 22
    grid = [[' ' for _ in range(W)] for _ in range(H)]
    
    def put_text(x, y, text):
        for i, c in enumerate(text):
            if 0 <= x+i < W and 0 <= y < H:
                grid[y][x+i] = c
                
    def put_center(x_center, y, text):
        start_x = x_center - len(text) // 2
        put_text(start_x, y, text)

    put_text(0, 21, "└" + "─"*78 + "┘")
    for y in range(0, 21):
        grid[y][0] = '│'
        grid[y][79] = '│'

    for i in range(20):
        sx = (i * 13 + int(scroll_offset * 2)) % 78 + 1
        sy = (i * 7 + int(scroll_offset)) % 20
        grid[sy][sx] = random.choice(['.', '·', '✦', '✧'])

    put_center(40, 3, "E N T E R   Y O U R   N A M E")
    put_center(40, 5, name_input + "_")
    
    put_center(40, 8,  "╭─────────────────────────────────╮")
    put_center(40, 9,  "│       H O W   T O   P L A Y     │")
    put_center(40, 10, "├─────────────────────────────────┤")
    put_center(40, 11, "│ 1. Read the math problem.       │")
    put_center(40, 12, "│ 2. Steer to the correct answer. │")
    put_center(40, 13, "│ 3. One wrong answer = Game Over.│")
    put_center(40, 14, "│                                 │")
    put_center(40, 15, "│ Use [← →] or [A/D] to steer.    │")
    put_center(40, 16, "╰─────────────────────────────────╯")

    put_center(40, 19, "[ ENTER ]  T O   S T A R T")

    output = ["".join(row) for row in grid]
    title = "\033[1;36m" + " " * 20 + "A R I T H M E T I C   R A C E R" + " " * 20 + "\033[0m"
    
    lines = [title]
    for row in output:
        row = row.replace(name_input + "_", f"\033[93m{name_input}_\033[36m")
        lines.append(row)
        
    sys.stdout.write('\033[H\033[J\033[36m' + "\n".join(lines) + '\033[0m')
    sys.stdout.flush()

def draw_frame(state, scroll_offset):
    W, H = 80, 22 
    grid = [[' ' for _ in range(W)] for _ in range(H)]

    def put_text(x, y, text):
        for i, c in enumerate(text):
            if 0 <= x+i < W and 0 <= y < H:
                grid[y][x+i] = c
                
    def put_center(x_center, y, text):
        start_x = x_center - len(text) // 2
        put_text(start_x, y, text)

    put_text(0, 21, "└" + "─"*47 + "┴" + "─"*30 + "┘")
    for y in range(0, 21):
        grid[y][0] = '│'
        grid[y][48] = '│'
        grid[y][79] = '│'

    for i in range(15):
        sx = (i * 13 + int(scroll_offset * 2)) % 46 + 1
        sy = (i * 7 + int(scroll_offset)) % 20
        if grid[sy][sx] == ' ':
            grid[sy][sx] = random.choice(['.', '·', '✦', '✧'])

    for y in range(0, 21):
        grid[y][16] = '║'
        grid[y][32] = '║'

    for y in range(0, 21):
        if (y + int(scroll_offset)) % 4 < 2:
            put_center(8, y, "- - -")
            put_center(24, y, "- - -")
            put_center(40, y, "- - -")

    put_text(49, 0, "╭" + "─"*29 + "╮")
    put_text(49, 1, "│" + " "*29 + "│")
    put_center(64, 1, state.q_text)
    
    ratio = max(0, state.time_left / state.total_time)
    bar = '▓' * int(15 * ratio) + '░' * (15 - int(15 * ratio))
    put_text(49, 2, f"│ {bar} {state.time_left:>4.1f}s  │")
    put_text(49, 3, "╰" + "─"*29 + "╯")

    put_text(49, 5, "╭" + "─"*29 + "╮")
    put_center(64, 6, "S T A T U S")
    put_text(49, 6, "│" + " "*29 + "│")
    put_text(49, 7, "├" + "─"*29 + "┤")
    
    mult = min(5.0, 1.0 + (state.question_num - 1) * 0.5)
    acc = int(state.correct_answers / max(1, state.question_num - 1) * 100) if state.question_num > 1 else 0
    speed = state.tier_idx * 20 + 10
    
    put_text(49, 8,  f"│ {'SCORE':<10}{state.score:>17,} │")
    put_text(49, 9,  f"│ {'MULTIPLIER':<10}{f'x{mult:.1f}':>17} │")
    put_text(49, 10, f"│ {'TIER':<10}{state.tier_idx + 1:>17} │")
    put_text(49, 11, f"│ {'SPEED':<10}{speed:>17.1f} │")
    put_text(49, 12, "├" + "─"*29 + "┤")
    put_text(49, 13, f"│ {'STREAK':<10}{state.correct_answers:>17} │")
    put_text(49, 14, f"│ {'ACCURACY':<10}{f'{acc}%':>17} │")
    put_text(49, 15, "├" + "─"*29 + "┤")
    put_text(49, 16, "│ [← →] Steer                 │")
    put_text(49, 17, "│ [P] Pause      [Q] Quit     │")
    put_text(49, 18, "╰" + "─"*29 + "╯")

    if not state.game_over:
        progress = 1.0 - (state.time_left / state.total_time)
        ans_y = int(0 + progress * 18) 
        if 0 <= ans_y <= 18:
            for i, opt in enumerate(state.options):
                box_str = f"[  {opt:^3}  ]"
                put_center([8, 24, 40][i], ans_y, box_str)

    px = int(8 + state.current_lane * 16)
    put_center(px, 18, f"({state.name})")
    put_center(px, 19, "||")
    put_center(px, 20, "▀▀▀▀")

    for p in state.particles:
        px = [8, 24, 40][p["lane"]]
        py = int(p["y"])
        if 0 <= py < 20:
            put_center(px, py, p["text"])

    if state.paused:
        put_center(40, 10, "╭─────────────────────────╮")
        put_center(40, 11, "│       P A U S E D       │")
        put_center(40, 12, "│  Press [P] to resume    │")
        put_center(40, 13, "╰─────────────────────────╯")

    if state.game_over:
        put_center(40, 8,  "╭─────────────────────────────────────────╮")
        put_center(40, 9,  "│           G A M E   O V E R             │")
        put_center(40, 10, "│                                         │")
        put_center(40, 11, f"│  FINAL SCORE:                   {state.score:>7,} │")
        put_center(40, 12, f"│  TIER REACHED:                       {state.tier_idx+1} │")
        put_center(40, 13, f"│  ACCURACY:                         {acc:>3}% │")
        put_center(40, 14, "│                                         │")
        put_center(40, 15, "│  [R] Restart          [Q] Quit          │")
        put_center(40, 16, "╰─────────────────────────────────────────╯")

    output = ["".join(row) for row in grid]
    title = "\033[1;36m" + " " * 20 + "A R I T H M E T I C   R A C E R" + " " * 20 + "\033[0m"
    
    lines = [title]
    for row in output:
        row = row.replace(f"({state.name})", f"\033[95m({state.name})\033[36m")
        for opt in state.options:
            row = row.replace(f"[  {opt:^3}  ]", f"\033[93m[  {opt:^3}  ]\033[36m")
        
        if state.paused:
            row = row.replace("P A U S E D", "\033[93mP A U S E D\033[36m")
            
        if state.game_over:
            row = row.replace("G A M E   O V E R", "\033[91mG A M E   O V E R\033[36m")
            row = row.replace("FINAL SCORE", "\033[91mFINAL SCORE\033[36m")
        lines.append(row)

    sys.stdout.write('\033[H\033[J\033[36m' + "\n".join(lines) + '\033[0m')
    sys.stdout.flush()