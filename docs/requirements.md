# Arithmetic Racer 2.0 — Requirements

## 1. Problem Statement

Arithmetic Racer 2.0 is a single-player arcade game that turns mental arithmetic
practice into a reaction challenge. The player is given an arithmetic problem and
three candidate answers, one per road lane. The answers travel toward the player
as the game timer counts down. The player must switch into the lane containing the
correct answer before the timer reaches zero.

A correct choice adds points, advances the question counter, and makes the next
question slightly faster. A wrong choice ends the run immediately.

## 2. Goals

- Provide fast, replayable mental-arithmetic practice with immediate feedback.
- Scale difficulty smoothly from single-digit addition to multiplication and
  larger operands.
- Keep the rules deterministic and testable without launching a graphical window.
- Keep the presentation readable at a glance: one question, three options, one
  timer bar, one lane choice.

## 3. Game Loop and State Machine

```text
START ──Enter/Space──▶ PLAYING ──P──▶ PAUSED
                          │              │
                          │◀────P────────┘
                          │
                     timer expires
                          │
                          ▼
                      GAME_OVER ──R──▶ PLAYING
                          │
                          └──Q──▶ exit
```

- **START** — the player types a name and starts the race. The background scrolls
  at the idle speed.
- **PLAYING** — the timer, lane animation, particles, and world scroll advance.
- **PAUSED** — the game timer, world scroll, stars, and trees all freeze. The pause
  overlay is drawn on top of the frozen frame.
- **GAME_OVER** — shown after a wrong lane choice or an expired timer on a wrong
  lane. The final score is displayed; the player can retry or quit.

## 4. Mathematical Model

The rules below define the game balance and are treated as an immutable contract.

### 4.1 Question timer

```text
T = D / (v0 * speed_multiplier)
```

- `T` — seconds available to answer the current question.
- `D` — distance dial for the current tier.
- `v0` — base scroll speed for the current tier.
- `speed_multiplier` — starts at `1.0`, increases by `0.06` after every correct
  answer, and is capped at `1.45`.

### 4.2 Score multiplier

```text
multiplier = min(5.0, 1.0 + (question_num - 1) * 0.5)
```

The multiplier is based on the number of questions answered, not on the number of
consecutive correct answers.

### 4.3 Points per correct answer

```text
points = int(base_score * multiplier)
```

### 4.4 Tier progression

| Tier | Question numbers | `v0` | `D` | Base score | Operations |
| --- | --- | --- | --- | --- | --- |
| 1 | 1–5 | 10 | 80 | 10 | `+` |
| 2 | 6–9 | 19 | 180 | 20 | `+` |
| 3 | 10–13 | 35 | 385 | 35 | `+`, `-` |
| 4 | 14–19 | 65 | 812 | 55 | `+`, `-`, `x` |
| 5 | 20+ | 120 | 1680 | 80 | `x` |

### 4.5 World scroll speed

```text
scroll_speed = (tier_index * 100 + 200) * speed_multiplier
```

The same value drives the background animation and the HUD `SPEED` readout. The
START screen uses a fixed idle speed of `100`.

### 4.6 Operand ranges

| Tier | Addition | Subtraction | Multiplication |
| --- | --- | --- | --- |
| 1 | 1–10 + 1–10 | — | — |
| 2 | 1–100 + 1–100 | — | — |
| 3 | 1–100 + 1–100 | `a` in 50–100, `b` in 1–50 | — |
| 4 | 1–999 + 1–999 | `a` in 500–999, `b` in 1–499 | 2–9 × 2–9 |
| 5 | — | — | 2–12 × 2–12 |

Subtraction is always constructed so the result is non-negative.

### 4.7 Answer options

- Each question has exactly three options: the correct answer plus two decoys.
- Decoys are generated with offsets `±1, ±2, ±10, ±20`.
- Decoys must be non-negative and unique.
- For answers of `20` or more, a decoy sharing the same final digit is rejected.
- Option order is shuffled, and `correct_lane` is the index of the correct answer.
- Generation must always terminate. The random attempt loop is capped; a
  deterministic fallback (`answer + 1`, `answer + 2`, …) guarantees three options.

## 5. Functional Requirements

| ID | Requirement |
| --- | --- |
| FR-01 | The game must start in the `START` state with a text-entry name prompt. |
| FR-02 | Names are trimmed, uppercased, and truncated to two characters. A one-character name is valid; a blank name falls back to `PL`. |
| FR-03 | Starting a game must create a fresh `GameState` with score `0`, question `1`, and speed multiplier `1.0`. |
| FR-04 | The three answer options must be rendered in lanes 0, 1, and 2. |
| FR-05 | Left/right input must move the target lane within `[0, 2]` and animate the player toward it. |
| FR-06 | The timer must decrease by the frame delta and resolve on or below zero. |
| FR-07 | A correct lane must award points, advance the question, raise the speed multiplier, and generate the next question. |
| FR-08 | A wrong lane must set `game_over` and stop the timer. |
| FR-09 | `P` must pause and resume. While paused, the background must not scroll. |
| FR-10 | `Q` must quit only on `GAME_OVER`; `Esc` may quit on `START`. It must never quit during `PLAYING` or `PAUSED`. |
| FR-11 | `R` must restart from `GAME_OVER`, preserving the entered name. |
| FR-12 | A missing `bike.png` must produce a clear error and terminate the program. |
| FR-13 | The window must remain 1280×600 at a 60 FPS target. |

## 6. Non-Functional Requirements

| ID | Requirement |
| --- | --- |
| NFR-01 | Runtime code must be exactly three Python modules: `config.py`, `game_state.py`, `pygame_main.py`. |
| NFR-02 | The only third-party runtime dependency is Pygame (`pygame-ce`). Tests use the standard library only. |
| NFR-03 | `game_state.py` must not import Pygame, so all rules are testable headlessly. |
| NFR-04 | All randomized balance rules must be reproducible with `random.seed(...)` in tests. |
| NFR-05 | The game must run offline and must not write save data. |
| NFR-06 | Rendering must keep the existing synthwave palette, perspective geometry, and draw order. |

## 7. Acceptance Criteria

1. `python pygame_main.py` opens the START screen and a typed name starts a race.
2. The HUD shows the current question, timer, score, multiplier, speed, and tier.
3. Choosing the correct lane repeatedly advances tiers at question numbers
   5/9/13/19 and caps the score multiplier at `x5.0`.
4. Letting the timer expire on a wrong lane shows GAME OVER; `R` restarts.
5. Pausing freezes the timer, lane motion, stars, forest, and road scroll.
6. `Q` does nothing during PLAYING/PAUSED and quits only on GAME_OVER.
7. `python -m unittest discover -s tests -v` passes without opening a window.
8. The game looks identical to the pre-refactor version apart from the intended
   stable skyline windows, the corrected HUD speed value, the gradient sun, the
   layered neon road lines, and the tree clearance spacing.

## 8. Out of Scope

- Multiplayer or networked play.
- Persistent high scores or player profiles.
- Audio.
- Additional art assets, themes, or game modes.
- Localization.
