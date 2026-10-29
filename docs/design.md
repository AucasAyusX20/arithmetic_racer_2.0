# Arithmetic Racer 2.0 — Design

## 1. Architecture Overview

The project uses a strict three-layer split. Each layer only depends on the layer
below it, and the rules layer has no knowledge of Pygame.

```text
┌──────────────────────────────────────────────┐
│                  config.py                   │
│  Difficulty "database": TIERS + pure helpers │
│  get_tier_index / get_multiplier / speed     │
└──────────────────────┬───────────────────────┘
                       │ imported by
┌──────────────────────▼───────────────────────┐
│                game_state.py                 │
│  GameState: questions, timer, score, lanes   │
│  No pygame import. Fully headless-testable.  │
└──────────────────────┬───────────────────────┘
                       │ read / updated by
┌──────────────────────▼───────────────────────┐
│                pygame_main.py                │
│  PygameRacer: event loop, world, rendering   │
└──────────────────────────────────────────────┘
```

### Responsibilities

| Module | Role | Owns | Must not own |
| --- | --- | --- | --- |
| `config.py` | Database + pure functions | Tier table, tier thresholds, multiplier and scroll-speed formulas | Mutable state, rendering |
| `game_state.py` | Brain | Current question, options, timer, score, lane choice, particles, pause/game-over flags | Pixels, fonts, input events |
| `pygame_main.py` | Dumb view | Window, input mapping, world animation, draw order, asset loading | Game rules, scoring formulas, tier logic |

The dependency direction is one-way: `pygame_main → game_state → config`. The
lower layers never import the layer above them.

## 2. Why This Split

- **Testability** — the complete rules engine can be exercised with `unittest`
  without creating an SDL window or loading an image.
- **Tunability** — balance changes are data edits in `config.py`; no rendering code
  is touched.
- **Replaceable presentation** — a terminal renderer or web client could drive the
  same `GameState` API.
- **Viva clarity** — the "database → brain → view" story maps directly to the
  code structure.

## 3. Data Flow

### Startup

1. `pygame_main.py` initializes Pygame, creates the 1280×600 window, and loads
   `bike.png` relative to the module's own path.
2. `PygameRacer.__init__` caches fonts and static surfaces, then generates the
   stars, skyline (including window lights), and 1,500 forest trees.
3. `GameState` is only created when the player starts a run.

### Per-frame loop

```text
clock.tick(60) ─▶ dt (clamped to 50 ms)
      │
      ├─▶ drain pygame events (name entry / lane / pause / retry / quit)
      │
      ├─▶ PygameRacer.update(dt)
      │      ├─ if paused: return immediately
      │      ├─ scroll_offset += scroll_speed * dt
      │      ├─ move stars and trees
      │      └─ GameState.update(dt)   (timer, lane easing, particles)
      │
      ├─▶ PygameRacer.draw()
      │      └─ world → answers → player → HUD → overlay
      │
      └─▶ pygame.display.flip()
```

`dt` is clamped to `0.05 s` so a stalled frame cannot teleport the player or drain
the timer in one step.

## 4. Game State Model

`GameState` fields:

| Field | Meaning |
| --- | --- |
| `name` | Trimmed, uppercased, max-2-character tag shown above the bike |
| `score` | Accumulated points |
| `question_num` | 1-based question counter; also drives tier and multiplier |
| `game_over` | Set by a wrong lane choice |
| `paused` | Set by the view's `P` key |
| `speed_multiplier` | `1.0` → `1.45`; shortens each question's timer |
| `tier_idx` | Current tier, derived from `question_num` |
| `target_lane` | Lane selected by the player (`0–2`) |
| `current_lane` | Float position for smooth easing toward `target_lane` |
| `total_time` | Timer value at question generation |
| `time_left` | Remaining time |
| `q_text`, `correct_answer` | Current problem and its answer |
| `options`, `correct_lane` | Shuffled three-way choice and the index of the answer |
| `particles` | Floating `+points` feedback records |

`reset()` rebuilds all per-run fields and generates the first question.
`GameState.update(dt)` early-returns when the run is paused or over, so a paused
game cannot lose time even if the view keeps calling `update`.

## 5. Question and Decoy Generation

1. Resolve the tier from `question_num`.
2. Compute `total_time` from the tier and the current speed multiplier.
3. Pick an allowed operator, build operands, and format `q_text`.
4. Build options:
   - Start with the correct answer.
   - Up to 25 attempts: take a random offset from `±1, ±2, ±10, ±20`, reject
     negative values, duplicates, and (for answers ≥ 20) decoys with the same final
     digit.
   - If the attempts are exhausted, append `answer + 1`, `answer + 2`, … until there
     are three unique options. This makes the loop provably finite.
5. Shuffle and record `correct_lane`.

The fallback is unreachable under ordinary randomness but removes the theoretical
infinite loop that the original `while len(options) < 3` loop allowed.

## 6. Scoring and Difficulty

- Correct answer: `points = int(base_score * get_multiplier(question_num))`.
- `question_num` increments after a correct answer.
- `speed_multiplier` grows by `0.06` per correct answer, capped at `1.45`.
- The next question's timer is `D / (v0 * speed_multiplier)`, so each success makes
  the following question shorter.
- A wrong answer (or an expired timer while in the wrong lane) sets `game_over`.
- The HUD's multiplier and speed call the same `config.py` helpers as the scoring
  and scrolling code, eliminating duplicate formulas.

## 7. Rendering Design

Draw order is fixed and matters:

1. Sky gradient, stars, city skyline and window lights, gradient sun, horizon line.
2. Perspective floor grid.
3. Forest floor polygons.
4. Road polygon, neon edges, centre line, dashed lane markers.
5. Trees, sorted back-to-front by depth.
6. Answer boxes (perspective interpolation from horizon to the player).
7. Player shadow, bike sprite, name badge.
8. HUD panel.
9. Pause or game-over overlay last.

### Perspective model

- Depth is normalized to `z ∈ (0, 1]`.
- Screen position uses `p = z ** 2.5`, giving dense detail near the horizon.
- Road width, tree size, and lane positions interpolate linearly in `p` between the
  horizon and the bottom of the screen.
- Answer boxes move from horizon-scale to full-size as the question timer drains:
  `p = (1 - time_left / total_time) ** 2`.

### Performance Caching

The gradient sun is expensive to draw (a scanline gradient loop, per-scanline
stripe cutouts, and a multi-layer glowing rim), yet it never changes from frame
to frame. It is therefore pre-rendered once at startup into `self.sun_canvas` by
`build_sun_canvas()`, a `SRCALPHA` surface that already contains:

1. the yellow-to-pink scanline gradient clipped to the disc's curve,
2. the `SKY_BOTTOM` stripe cutouts, each row clipped to the sun's silhouette,
3. a glowing rim built from 24 vertical bands (yellow crown fading to pink base)
   and per-pixel alpha halo rings (alpha `12 → 255`) that fade into a crisp
   colored core edge.

Every frame `draw_sky_and_sun()` performs a single `screen.blit()` of that
canvas, so none of the scanline or rim work runs inside the 60 FPS loop.

### The `neon_line()` glow helper

`neon_line()` creates a neon glow from plain opaque draws, with no per-frame
alpha surfaces: it strokes the same line four times, each pass wider and dimmer
(`width + 14 / +9 / +5 / +0` with brightness factors `0.16 / 0.32 / 0.55 / 1.0`).
The wide, dark halo layers read as a soft bloom around the bright core line,
which stays crisp. The road shoulders and centre line both use it.

### Performance choices

- **Cached fonts** — all fixed sizes are created once in `__init__`; the continuously
  scaled answer text uses a pre-built size ramp (`1–40 px`).
- **Cached surfaces** — the bike shadow and the pause/game-over overlays are built
  once instead of every frame.
- **Stable skyline** — window coordinates are generated once in `__init__`. The old
  code re-rolled them every frame, causing a visible flicker.
- **Absolute asset path** — `Path(__file__).resolve().parent / "bike.png"` works
  regardless of the current working directory.

Tree sorting (1,500 entries per frame) is retained because back-to-front order is
required for correct overlap; the list is small enough for the 60 FPS target.

Tree placement uses a "setback and shoulder" rule so the forest can never cover
the road markings. For a tree at depth `p` with canopy width `tw`:

- `setback = tw * 0.5 + shoulder`, where `shoulder = 12 + p * 30`, is the minimum
  distance from the road edge to the tree centre, so even the widest canopy row
  stays clear of the glowing border.
- the remaining horizontal space beside the road is reduced by the setback and
  one canopy half-width, which keeps the whole tree (not just its centre) inside
  the screen.

Because the road widens toward the bottom of the screen while the canopy widens
upward from its base, the base row is always the tightest fit; the formula holds
at every depth and scale, giving roughly 18 px of clearance between the nearest
canopy and the road edge.

## 8. Input and State Transitions

| Current state | Input | Next state / effect |
| --- | --- | --- |
| START | `Enter` / `Space` | Create `GameState`, go to PLAYING |
| START | `Esc` | Exit |
| START | alphanumeric / Backspace | Edit name (max 10 chars) |
| PLAYING | `←`/`A`, `→`/`D` | Change `target_lane` within `[0, 2]` |
| PLAYING | `P` | PAUSED (`state.paused = True`) |
| PAUSED | `P` | PLAYING (`state.paused = False`) |
| PLAYING | timer expires | Resolve lane → PLAYING (next question) or GAME_OVER |
| GAME_OVER | `R` | New `GameState`, PLAYING |
| GAME_OVER | `Q` | Exit |
| any | window close | Exit |

`Q` is deliberately not bound in PLAYING or PAUSED, preventing accidental
mid-race quits. On START, `Q` remains a legal name character; `Esc` is the quit
key there.

## 9. Error Handling

- A missing or unreadable `bike.png` raises `SystemExit` with the absolute path in
  the message.
- `pygame.QUIT` is always handled, independent of the game state.
- The pause guard exists in both layers: the view stops advancing the world and
  `GameState.update` ignores timer updates.

## 10. Testing Strategy

- `tests/test_game_state.py` imports only `config` and `game_state`.
- A `sys.path` shim points at the repository root so `unittest discover` works from
  anywhere in the tree.
- Seeded `random` makes decoy tests reproducible.
- Tests cover:
  - tier boundaries and multiplier cap,
  - the exact time formula for all five tiers,
  - score accumulation, speed-multiplier ramp and cap,
  - wrong-lane game over and paused-timer behaviour,
  - name normalization including the one-character case,
  - decoy validity over many generated questions,
  - the decoy fallback path via a patched RNG.
- A headless smoke test (`SDL_VIDEODRIVER=dummy`) can render every screen without a
  physical display.

## 11. Invariants

1. `0 <= target_lane <= 2` and `0 <= correct_lane <= 2`.
2. `options` always has three unique, non-negative values and contains
   `correct_answer`.
3. `correct_lane == options.index(correct_answer)`.
4. `time_left <= total_time` and `total_time > 0`.
5. `1.0 <= speed_multiplier <= 1.45`.
6. A paused or finished game never changes `time_left`.
7. The window is always 1280×600, and all perspective constants are unchanged.
