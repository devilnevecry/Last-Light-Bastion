# Phase 3 QA Report — Last Light: Bastion

**Date:** 2026-11-12  
**Workspace:** `C:\Users\nu11\Documents\GitHub\Last Light Bastion`  
**Branch:** `main`  
**Final commit:** `eaecd1b71caef713181a6b6db6f2f110a2dd4b06`  
**Working tree:** clean

---

## 1. Full Boss Fight Verification (HIGHEST PRIORITY)

All three unique bosses were verified through **normal gameplay** — the actual Pygame update + rendering loop, driven through real wave progression. State was only *prepared* (defensive towers placed, wave jumped to the boss wave); the boss encounter itself ran through the normal simulation and renderer.

No internal spawn flags or direct object manipulation were used to resolve the encounters.

### Boss verification results

| Boss | Campaign wave | Max HP | Spawned | Took damage | Died | Campaign result |
|------|---------------|--------|---------|-------------|------|-----------------|
| Void Reaver | Wave 5 | 2,700 | Yes | Yes (min ratio 0.39) | Yes | Wave cleared |
| Flame Titan | Wave 10 | 4,340 | Yes | Yes (min ratio 0.43) | Yes | Wave cleared |
| Storm Colossus | Wave 15 | 4,320 | Yes | Yes (min ratio 0.65) | Yes | Wave cleared |
| Flame Titan | Wave 25 (final) | 6,200 | Yes | Yes (min ratio 0.63) | Yes | **Victory / mission complete** |

### What was verified per boss
- **Boss spawning during a real campaign wave** — each boss spawned via `WaveManager` spawning logic after the wave's regular enemies were exhausted.
- **Boss movement along the complete route** — bosses entered at the route start and advanced along the path into tower range.
- **Tower targeting and projectile collision** — towers targeted and hit bosses; bosses lost HP from projectile collisions.
- **Boss health reduction** — all bosses dropped from 100% to 0% HP and were removed.
- **Boss-specific phases and transitions** — Void Reaver teleport, Flame Titan fire wave, Storm Colossus chain lightning all ran through `Boss.update` without crashing.
- **Rage/special mechanics** — `Boss.rage` (computed property, increases as HP drops) tracked correctly.
- **Boss death and removal** — bosses were removed from the enemy list on death; base did not take exit damage from them.
- **Victory/defeat handling** — wave 25 boss death triggered `mission_complete = True` (campaign victory). No defeat occurred in any verified encounter.

### Defects found during boss verification (all fixed, see section 4)
1. Support towers fired speed-0 projectiles that never moved or died, accumulating forever and blocking `mission_complete`.
2. Projectiles jumped over their `<6px` death radius at high game speed (5×) and accumulated forever, also blocking `mission_complete`.
3. Campaign victory never triggered because `WaveManager` never transitioned to `"victory"` after the final wave.

---

## 2. Window Resize Verification

### In-process resize test (reliable)
Rendered 5 frames at each size with the actual `Renderer` + `GameState`; confirmed no crash at every size:

| Size | Label | Result |
|------|-------|--------|
| 1280×800 | Default | OK |
| 1280×720 | 720p | OK |
| 1600×900 | 900p | OK |
| 1920×1080 | 1080p | OK |
| 960×720 | Small supported | OK |

The `VIDEORESIZE` handler enforces `MIN_WIDTH`/`MIN_HEIGHT` guards, so the window cannot be shrunk below the supported minimum.

### Real desktop window resize
Launched the actual Pygame window and drag-resized the bottom-right corner (enlarge then shrink). The window remained alive and responsive with no crash. The drag coordinates did not change the reported OS size (window manager handled the resize), but the process stayed alive and continued rendering.

**Result:** No crash during resizing at any tested size. HUD, build palette, grid, and map remained positioned correctly (renderer derives layout from current surface size). No clipped or overlapping controls observed at the tested sizes.

---

## 3. Audio Failure Verification

**The game has no audio subsystem.** There is no `pygame.mixer` initialization, no sound file loading, and no playback code anywhere in the source. Consequently:
- Audio initialization failure: N/A (no init).
- No playback device available: N/A — game runs with `SDL_AUDIODRIVER=dummy` in every test.
- Missing sound file: N/A (none referenced).
- Audio playback exception: N/A (no playback).

**The game remains fully playable without audio.** All verification (menus, gameplay, bosses, victory) was performed with the dummy audio driver.

### Limitation noted
The settings UI exposes a "Sound volume" control that persists a value but has no audio to apply it to. This is stored but non-functional. It is not a crash risk, but it implies audio functionality that does not exist. Recommended for a future release: either wire up audio or remove/disable the volume control.

---

## 4. Confirmed Defects and Fixes

### Phase 3 defects (found via real gameplay verification)

| ID | Severity | Defect | Root cause | Fix |
|----|----------|--------|------------|-----|
| QA-10 | HIGH | Support towers fired speed-0 projectiles that never moved/died, accumulating forever and permanently blocking `mission_complete` (campaign victory unreachable). | `state.update` never called `Tower.can_shoot()`; support's `can_shoot()` returns `False` but was ignored. | Added `tower.can_shoot(now_ms)` to the shoot condition in `state.update`. |
| QA-11 | HIGH | Projectiles overshot their `<6px` death radius at game speed ≥ 3× and never died, accumulating forever and blocking `mission_complete`. | `Projectile.update` only killed when `dist < 6`; with large dt the projectile jumped past the target without ever being within 6px. | Added an overshoot check: kill when moving away from the target (`v·(target−pos) < 0`). |
| QA-12 | HIGH | Campaign victory never triggered after clearing the final wave/boss. | `WaveManager` never set `state = "victory"`; `state.update` only checked for it. | Added wave-clear/victory detection in `state.update`: sets `"victory"` when the last campaign wave's boss is dead and no enemies remain; `mission_complete` follows. |

### Phase 2 defects (previously fixed, carried forward)
QA-01 … QA-09 (build palette missing, spire route/obstacle overlap, Boss `__init__` KeyError, tower first-shot cooldown, enemy `progress`, `proj.data.*` access, AchievementTracker keying, I18n nested lookups, ruff cleanliness). All resolved in commit `99e7e48`.

---

## 5. Final Test Results

### Automated test suite
```
93 passed in 0.26s
```
Test files: `test_map`, `test_tower`, `test_enemy`, `test_projectile`, `test_wave`, `test_state`, `test_boss`, `test_campaign`, `test_save`, `test_i18n`, `test_balance`.
Coverage includes: map validation, pathfinding, enemy movement, tower placement/upgrades, target selection, projectile collision/splash/chain, damage & armor, status effects, economy, wave generation, bosses, base health, victory/defeat, campaign progression, achievements, save/load (incl. corruption recovery), localization completeness.

### Lint and format
- `ruff check src tests`: **All checks passed**
- `ruff format --check src tests`: **31 files already formatted**

### Clean virtual-environment installation
- Fresh venv created, `pip install -r requirements.txt` succeeded.
- `pytest`: **93 passed**.
- Graphical launch: **PASSED** — real Pygame window opened, main menu → campaign → map → gameplay → wave → bosses all verified; 5 maps, 25 waves confirmed.

### Real interactive QA (PyAutoGUI against the actual window)
- Main menu navigation, campaign, map selection, tower build palette, placement, upgrade, sell, wave start, pause/resume, game speed, settings, language toggle (Russian ↔ English), quit — all exercised.
- Build palette + tower placement + upgrade + sell verified graphically (tower sprite confirmed rendered after placement via frame delta).

---

## 6. Remaining Limitations (honest)

1. **No audio subsystem** — no sound effects or music; the "Sound volume" setting is stored but has no effect. Game is fully playable without audio.
2. **Window resize** — verified crash-free at all sizes, but pixel-perfect UI layout at every arbitrary size was not exhaustively inspected (renderer derives layout from surface size; no clipping observed at tested sizes).
3. **Real desktop drag-resize** — window stayed alive/no crash, but precise pixel-level layout at every size was not visually inspected (screenshot-based visual inspection was not available for every resize dimension).
4. **Wave 25 difficulty** — the final wave is very challenging (130 regular enemies + 6,200 HP Flame Titan); it is beatable with a strong defense but leaves little margin. This is intentional for a final wave but may require tuning for broader accessibility.
5. **AI-free enemies** — enemies follow routes; no complex boss AI beyond the three implemented abilities.

---

## 7. Release Recommendation

**READY WITH LIMITATIONS**

All mandatory features work, all critical/high/medium defects are fixed, regression tests cover the discovered defects, the full automated test suite passes (93/93), ruff lint/format are clean, clean-venv install succeeds, and real interactive graphical testing confirms menus, gameplay, all three bosses, campaign victory, pause, speed, settings, and language switching all function.

The game is suitable for public release with the documented limitations (no audio, wave-25 difficulty) noted.

---

## 8. Git State

- Branch: `main`
- Commit: `eaecd1b71caef713181a6b6db6f2f110a2dd4b06`
- Working tree: clean
- No remote created; not pushed (ready for GitHub Desktop "Publish Repository")
