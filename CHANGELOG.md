# Changelog

All notable changes to Arithmetic Racer 2.0 are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-10-26

Visual polish pass on `pygame_main.py` only. Game balance, rules, scoring,
collision resolution, perspective constants, and the 60 FPS target are unchanged.

### Added

- `build_sun_canvas()` — renders the gradient sun once into a reusable
  `self.sun_canvas` surface; every frame only blits it, so the scanline gradient
  and stripe loops never run in the 60 FPS loop.
- `neon_line()` layered glow helper — stacks wide dim halo layers down to a
  bright core to fake a glow without per-frame alpha surfaces.
- Dynamic tree canopy spacing in `draw_forest()` — every tree is pushed past its
  own canopy half-width plus a perspective-scaled shoulder before spreading into
  the space left beside the road, and the distribution stays on-screen.

### Changed

- The sun is now a yellow-to-pink scanline gradient with 24 vertical glow bands
  and retro `SKY_BOTTOM` stripe cutouts that start below the crown.
- Road shoulders and the centre line are stroked with the layered `neon_line()`
  glow instead of flat single-pass lines.
- Lane dashes follow their lane's perspective slope and use a wider thickness
  ramp (4–14 px) so they stay clearly visible at every depth.

### Fixed

- Road lane dashes now keep a consistent depth-space rhythm instead of
  stretching into large empty gaps near the player.
- Trees no longer overlap the road boundaries; the setback and shoulder math
  guarantees roughly 18 px of clearance between the nearest canopy and the road
  edge at any depth.

## [2.1.0] - 2026-10-26

Professional refactor for the college presentation. Game balance, visuals, and the
three-module architecture are unchanged; the work below is documentation, hygiene,
bug fixes, and performance cleanup.

### Added

- `README.md` with setup, run instructions, controls, and project layout.
- `docs/requirements.md` with the mathematical contract, requirements IDs, and
  acceptance criteria.
- `docs/design.md` with the layered architecture, data flow, rendering pipeline, and
  design rationale.
- `tests/test_game_state.py` — a headless `unittest` suite covering tier boundaries,
  the time formula, scoring, the speed-multiplier cap, name handling, decoy
  invariants, and the decoy fallback.
- `requirements.txt` pinned to `pygame-ce==2.5.8`.
- `.gitignore` for Python caches, virtual environments, and editor/OS noise.
- `IDLE_SCROLL_SPEED`, `MULTIPLIER_STEP`, `MULTIPLIER_CAP`, and
  `get_scroll_speed()` in `config.py` as single sources of truth.

### Changed

- The HUD multiplier now calls `get_multiplier()` instead of duplicating the formula.
- The HUD speed now derives from the real world scroll formula
  `(tier * 100 + 200) * speed_multiplier` instead of `tier * 20 + 10`.
- All fixed-size fonts and the scaled answer-font ramp are cached in `__init__`.
- The pause and game-over overlays and the bike shadow surface are cached.
- City skyline window lights are generated once at startup.
- `bike.png` is loaded through an absolute path based on `Path(__file__)`.
- Quit behaviour is now state-aware: `Esc` on START, `Q` on GAME_OVER, and no quit
  binding during PLAYING/PAUSED.
- `GameState.update()` and `PygameRacer.update()` both respect pause, freezing the
  timer and the entire background.

### Fixed

- Tree recycling now replaces the list element (`self.trees[i] = ...`) instead of
  mutating the dictionary with `dict.update()`.
- Decoy generation is capped at 25 random attempts with a deterministic
  `answer + 1, answer + 2, …` fallback, eliminating a theoretical infinite loop.
- One-character player names are now preserved (`"A"` instead of falling back to
  `"PL"`).
- Skyline window flicker caused by per-frame randomization.
- The background scrolling while paused.
- Accidental mid-race quits via `Q`.

### Removed

- The duplicated inline multiplier expression in the HUD.
- The fake HUD speed formula.
- Per-frame `pygame.font.SysFont` allocation.
- The unused `correct_answers` counter.
- Dead conditionals and redundant re-computation in `resolve_collision()`.

### Unchanged

- `T = D / (v0 * speed_multiplier)` and all tier values.
- Tier thresholds, base scores, score formula, and the `+0.06` / `1.45` speed ramp.
- Decoy offsets and the same-final-digit rejection rule.
- All rendering geometry, palette, draw order, and the 1280×600 window.

[2.2.0]: https://github.com/AucasAyusX20/arithmetic_racer_2.0/releases/tag/v2.2.0
[2.1.0]: https://github.com/AucasAyusX20/arithmetic_racer_2.0/releases/tag/v2.1.0
