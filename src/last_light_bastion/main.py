"""Last Light: Bastion - main application entry point and game loop."""

from __future__ import annotations

import pygame
from campaign import AchievementTracker, Campaign
from config import (
    BASE_HEIGHT,
    BASE_WIDTH,
    FPS_TARGET,
    GAME_SPEEDS,
    MAP_ORDER,
    MIN_HEIGHT,
    MIN_WIDTH,
    STAR_THRESHOLDS,
    TOWER_BASE_COSTS,
)
from i18n import I18n
from renderer import Renderer
from save import load as load_save
from save import save as save_save
from settings import Settings
from state import GameState
from ui import UI


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Last Light: Bastion")
        self.screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True

        save_data = load_save()
        self.settings = Settings(save_data)
        self.i18n = I18n(self.settings.language)
        self.campaign = Campaign(save_data)
        self.achievements = AchievementTracker(self.campaign)

        self.state = GameState()
        self.ui = UI(self.campaign, self.settings, self.i18n)
        self.renderer = Renderer(self.screen, self.state)

        # tower build palette order
        self.build_order = ["archer", "cannon", "frost", "arc", "poison", "support"]

    # ------------------------------------------------------------------ run
    def run(self) -> None:
        while self.running:
            dt_ms = self.clock.tick(FPS_TARGET)
            self._handle_events()
            self._update(dt_ms)
            self.renderer.draw(self.state, self.ui, self.i18n)
            pygame.display.flip()
        self._shutdown()

    # ------------------------------------------------------------- events
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._on_keydown(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._on_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                self._on_mouse_move(event.pos)
            elif event.type == pygame.VIDEORESIZE:
                self._on_resize(event.w, event.h)

    def _on_keydown(self, key: int) -> None:
        ui = self.ui
        if ui.state == "playing":
            if key == pygame.K_ESCAPE:
                ui.state = "paused"
            elif key == pygame.K_SPACE:
                self._toggle_wave()
            elif key == pygame.K_1:
                self._set_speed(GAME_SPEEDS[0])
            elif key == pygame.K_2:
                self._set_speed(GAME_SPEEDS[1])
            elif key == pygame.K_3:
                self._set_speed(GAME_SPEEDS[2])
            elif key == pygame.K_4:
                self._set_speed(GAME_SPEEDS[3])
            elif key == pygame.K_5:
                self._set_speed(GAME_SPEEDS[4])
            elif key == pygame.K_p:
                ui.state = "paused"
        elif ui.state == "paused":
            if key in (pygame.K_ESCAPE, pygame.K_p):
                ui.state = "playing"
        elif ui.state == "results":
            if key in (pygame.K_ESCAPE, pygame.K_RETURN):
                ui.to_main_menu()

    def _on_click(self, pos) -> None:
        ui = self.ui
        state = self.state
        i18n = self.i18n
        x, y = pos
        w, h = self.screen.get_size()

        if ui.state == "main_menu":
            self._handle_main_menu_click(x, y, w, h)
        elif ui.state == "campaign":
            self._handle_campaign_click(x, y, w, h)
        elif ui.state == "settings":
            self._handle_settings_click(x, y, w, h)
        elif ui.state == "achievements":
            self._handle_achievements_click(x, y, w, h)
        elif ui.state == "playing":
            self._handle_playing_click(x, y, state, i18n)
        elif ui.state == "paused":
            self._handle_paused_click(x, y, w, h)
        elif ui.state == "results":
            self._handle_results_click(x, y, w, h)

    def _on_mouse_move(self, pos) -> None:
        if self.ui.state == "main_menu":
            x, y = pos
            w, h = self.screen.get_size()
            cx = w // 2
            btns = ["play", "campaign", "endless", "achievements", "settings", "quit"]
            for i, key in enumerate(btns):
                by = h // 2 - 70 + i * 52
                if cx - 140 <= x <= cx + 140 and by <= y <= by + 44:
                    self.ui.hover = key
                    return
            self.ui.hover = ""

    def _on_resize(self, w: int, h: int) -> None:
        w = max(MIN_WIDTH, w)
        h = max(MIN_HEIGHT, h)
        self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)

    # ------------------------------------------------------------- menu clicks
    def _handle_main_menu_click(self, x, y, w, h) -> None:
        cx = w // 2
        cy = h // 2
        btns = ["play", "campaign", "endless", "achievements", "settings", "quit"]
        for i, key in enumerate(btns):
            by = cy - 70 + i * 52
            if cx - 140 <= x <= cx + 140 and by <= y <= by + 44:
                if key == "play":
                    self.ui.to_campaign()
                elif key == "campaign":
                    self.ui.to_campaign()
                elif key == "endless":
                    self.ui.start_endless(self.state)
                elif key == "achievements":
                    self.ui.to_achievements()
                elif key == "settings":
                    self.ui.to_settings()
                elif key == "quit":
                    self.running = False
                return

    def _handle_campaign_click(self, x, y, w, h) -> None:
        # back not present; clicking a map starts it
        for i, key in enumerate(MAP_ORDER):
            col = i % 3
            row = i // 3
            bx = 100 + col * 390
            by = 110 + row * 210
            if bx <= x <= bx + 350 and by <= y <= by + 180:
                if self.ui.campaign.is_unlocked(key):
                    self.ui.start_map(key, self.state)
                return

    def _handle_settings_click(self, x, y, w, h) -> None:
        # language / volume / fullscreen toggles by approximate region
        if w // 2 - 100 <= x <= w // 2 + 100 and h - 80 <= y <= h - 36:
            self.ui.to_main_menu()
            return
        # cycle language
        if 120 <= x <= 300:
            if 125 <= y <= 155:
                self._cycle_language()
            elif 177 <= y <= 207:
                self.settings.volume = round(max(0.0, self.settings.volume - 0.1), 1)
                save_save(self.campaign.save)
            elif 229 <= y <= 259:
                self.settings.fullscreen = not self.settings.fullscreen
                save_save(self.campaign.save)

    def _handle_achievements_click(self, x, y, w, h) -> None:
        if w // 2 - 100 <= x <= w // 2 + 100 and h - 55 <= y <= h - 11:
            self.ui.to_main_menu()

    def _handle_playing_click(self, x, y, state, i18n) -> None:
        # HUD next wave button area top-right
        w, _ = self.screen.get_size()
        # tower panel buttons
        if state.selected_tower:
            px = w - 210 - 20
            py = 80
            # compute panel bottom buttons similar to renderer
            yy = py + 40 + 3 * 22 + 6 + 30
            if px + 12 <= x <= px + 107 and yy <= y <= yy + 30:
                self._upgrade_selected()
                return
            if px + 114 <= x <= px + 198 and yy <= y <= yy + 30:
                self._sell_selected()
                return
        # build palette (below grid)
        ox, oy = state.grid_offset
        ts = state.tile_size
        bar_y = oy + state.map.rows * ts + 10
        by = bar_y + 10
        bx = ox + 110
        btn_w = 100
        for i, tower_id in enumerate(["archer", "cannon", "frost", "arc", "poison", "support"]):
            btn_x = bx + i * (btn_w + 10)
            if btn_x <= x <= btn_x + btn_w - 8 and by <= y <= by + 58:
                if state.currency >= TOWER_BASE_COSTS[tower_id]:
                    state.start_placement(tower_id)
                return
        # grid click
        gx, gy = state.pixel_to_grid(x, y)
        if state.placement_mode:
            if state.try_place_tower(gx, gy):
                return
        tower = state.select_tower_at(gx, gy)
        if tower is not None:
            return
        # cancel placement if clicked empty
        if state.placement_mode:
            state.cancel_placement()

    def _handle_paused_click(self, x, y, w, h) -> None:
        if w // 2 - 90 <= x <= w // 2 + 90 and h // 2 + 30 <= y <= h // 2 + 70:
            self.ui.state = "playing"

    def _handle_results_click(self, x, y, w, h) -> None:
        if w // 2 - 100 <= x <= w // 2 + 100 and h // 2 + 50 <= y <= h // 2 + 94:
            self.ui.to_main_menu()

    # ------------------------------------------------------------- actions
    def _cycle_language(self) -> None:
        new_lang = "en" if self.settings.language == "ru" else "ru"
        self.settings.language = new_lang
        self.i18n.set_language(new_lang)
        save_save(self.campaign.save)

    def _toggle_wave(self) -> None:
        wm = self.state.wave_manager
        if wm.state in ("intermission", "idle"):
            wm.next_wave()

    def _set_speed(self, speed: float) -> None:
        self.state.set_speed(speed)
        self.settings.game_speed = speed
        save_save(self.campaign.save)

    def _upgrade_selected(self) -> None:
        if self.state.upgrade_selected():
            save_save(self.campaign.save)

    def _sell_selected(self) -> None:
        self.state.sell_selected()

    # ------------------------------------------------------------- update
    def _update(self, dt_ms: float) -> None:
        ui = self.ui
        state = self.state
        if ui.state == "playing":
            state.update(dt_ms)
            self._check_wave_complete()
            self._check_defeat()
            self._check_achievements()
        elif ui.state == "paused":
            pass

    def _check_wave_complete(self) -> None:
        state = self.state
        wm = state.wave_manager
        if wm.state == "victory" and not state.enemies and not state.projectiles:
            if not state.mission_complete:
                state.mission_complete = True
                self._award_mission()

    def _check_defeat(self) -> None:
        state = self.state
        if state.defeated and not self.ui.state == "results":
            self.ui.show_results(False, 0)

    def _award_mission(self) -> None:
        state = self.state
        ui = self.ui
        remaining = state.base_health
        pct = remaining / state.base_max_health if state.base_max_health else 0
        stars = sum(1 for t in STAR_THRESHOLDS if pct * 100 >= t)
        ui.stars = stars
        score = int(state.currency + remaining * 10 + stars * 100)
        self.ui.campaign.complete_map(state.map_key, stars, score)
        self._check_achievements()
        self.ui.show_results(True, stars)
        save_save(self.campaign.save)

    def _check_achievements(self) -> None:
        state = self.state
        rs = state.run_stats
        ctx = {
            "kills_total": self.campaign.total_kills + rs["kills"],
            "towers_built": self.campaign.total_towers_built + rs["towers_built"],
            "towers_built_run": rs["towers_built"],
            "tower_types_built": len(self.campaign.stats.get("tower_types_built", [])) | len(rs["tower_types_built"]),
            "max_tower_level": max((t.level for t in state.towers), default=1),
            "waves_survived": rs["waves_survived"],
            "bosses_defeated": self.campaign.total_bosses_defeated + rs["bosses_defeated"],
            "damage_taken": rs["damage_taken"],
            "mission_complete": state.mission_complete,
            "currency_peak": rs["max_currency"],
            "endless_wave": self.campaign.best_endless_wave,
            "flying_kills": self.campaign.stats.get("flying_kills", 0) + rs["flying_kills"],
            "campaign_complete": all(
                self.ui.campaign.is_completed(k) for k in __import__("config", fromlist=["MAP_ORDER"]).MAP_ORDER
            ),
        }
        for aid, data in __import__("config", fromlist=["ACHIEVEMENTS"]).ACHIEVEMENTS.items():
            cond = data.get("condition", "False")
            self.achievements.check(aid, cond, ctx)

    # ------------------------------------------------------------- shutdown
    def _shutdown(self) -> None:
        save_save(self.campaign.save)
        pygame.quit()


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
