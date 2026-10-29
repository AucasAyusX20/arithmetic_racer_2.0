# Arithmetic Racer 2.0

A neon synthwave arcade racer that turns mental arithmetic into a lane-switching
sprint. Solve the problem shown in the HUD and steer into the lane holding the
correct answer before the timer runs out — a wrong lane ends the run.

The world is drawn entirely with Pygame primitives: a striped retro sun, a
parallax city skyline, a perspective road grid, and a forest that rushes past the
camera. No third-party assets are required beyond `bike.png`.

## Features

- Five difficulty tiers that introduce subtraction and multiplication.
- A time limit derived from the tier's distance and scroll speed:
  `T = D / (v0 * multiplier)`.
- Streak-based score multiplier (up to `x5.0`) and a speed ramp for each correct
  answer.
- Keyboard-only controls, pause support, and a local retry loop.
- Game rules are fully decoupled from Pygame and covered by headless unit tests.

## Requirements

- Python 3.10+
- `pygame-ce` (imported as `pygame`)

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
python pygame_main.py
```

## Controls

| Screen | Key | Action |
| --- | --- | --- |
| START | `A-Z`, `0-9` | Type a player name (max 10 characters) |
| START | `Backspace` | Delete the last character |
| START | `Enter` / `Space` | Start the race |
| START | `Esc` | Quit |
| PLAYING | `←` / `A` | Move one lane left |
| PLAYING | `→` / `D` | Move one lane right |
| PLAYING | `P` | Pause / resume |
| PAUSED | `P` | Resume |
| GAME OVER | `R` | Retry with the same name |
| GAME OVER | `Q` | Quit |

`Q` is intentionally ignored during a race so a mistyped key cannot end the run.

## Project Structure

```text
arithmetic_racer_2.0/
├── config.py            # Difficulty tiers and shared pure functions
├── game_state.py        # Rules, scoring, question generation (no pygame)
├── pygame_main.py       # Input handling and rendering
├── bike.png             # Player sprite
├── docs/
│   ├── requirements.md  # Problem statement, goals and constraints
│   └── design.md        # Architecture and design decisions
├── tests/
│   └── test_game_state.py
├── requirements.txt
├── CHANGELOG.md
└── README.md
```

## Tests

The logic layer has no Pygame dependency, so the suite runs without opening a
window:

```bash
python -m unittest discover -s tests -v
```

## Documentation

- [Requirements](docs/requirements.md)
- [Design](docs/design.md)
- [Changelog](CHANGELOG.md)

## License

Released under the MIT License. See [LICENSE](LICENSE).
