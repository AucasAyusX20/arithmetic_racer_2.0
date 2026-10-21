# main.py
import time
import os
import sys

from config import *
from game_state import GameState
from renderer import clear_screen, draw_frame, draw_start_screen

if os.name == 'nt':
    import msvcrt
    def get_key():
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch == b'\xe0':
                ch = msvcrt.getch()
                if ch == b'K': return 'LEFT'
                if ch == b'M': return 'RIGHT'
            if ch == b'\r': return 'ENTER'
            if ch == b'\x08': return 'BACKSPACE'
            return ch.decode('utf-8', errors='ignore').upper()
        return None
else:
    import select
    import termios
    import tty
    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            r, _, _ = select.select([sys.stdin], [], [], 0)
            if r:
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    ch2 = sys.stdin.read(1)
                    ch3 = sys.stdin.read(1)
                    if ch2 == '[':
                        if ch3 == 'D': return 'LEFT'
                        if ch3 == 'C': return 'RIGHT'
                if ch == '\r' or ch == '\n': return 'ENTER'
                if ch == '\x7f': return 'BACKSPACE'
                return ch.upper()
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def main():
    sys.stdout.write('\033[?1049h')
    sys.stdout.write('\033[?25l') 
    
    name_input = ""
    scroll_offset = 0.0
    app_state = "START"
    
    while app_state == "START":
        draw_start_screen(name_input, scroll_offset)
        scroll_offset += 0.2
        
        key = get_key()
        if key:
            if key == 'ENTER':
                app_state = "PLAYING"
            elif key == 'BACKSPACE':
                name_input = name_input[:-1]
            elif key.isalnum() and len(name_input) < 10:
                name_input += key

        time.sleep(0.033)

    state = GameState(name_input)
    last_time = time.time()
    scroll_offset = 0.0
    running = True
    
    try:
        while running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            key = get_key()
            if key:
                if key == 'Q': 
                    running = False
                elif key == 'P' and not state.game_over: 
                    state.paused = not state.paused
                elif key in ['LEFT', 'A', '1']: 
                    if not state.paused and not state.game_over:
                        state.target_lane = max(0, state.target_lane - 1)
                elif key in ['RIGHT', 'D', '3']: 
                    if not state.paused and not state.game_over:
                        state.target_lane = min(2, state.target_lane + 1)
                elif key == '2': 
                    if not state.paused and not state.game_over:
                        state.target_lane = 1
                elif key == 'R' and state.game_over:
                    state.reset()
                    last_time = time.time()

            if not state.game_over and not state.paused:
                state.update(dt)
                scroll_offset += (state.tier_idx * 10 + 10) * state.speed_multiplier * dt * 2

            draw_frame(state, scroll_offset)

            time.sleep(max(0, 0.033 - (time.time() - current_time)))
            
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write('\033[?25h')
        sys.stdout.write('\033[?1049l') 
        print("Thanks for playing!")

if __name__ == "__main__":
    main()