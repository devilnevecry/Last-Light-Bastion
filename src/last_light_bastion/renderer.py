"""Renderer: draws the game using programmatic graphics, independent of simulation."""

from __future__ import annotations

import pygame
from config import (
    ACHIEVEMENTS,
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_DANGER,
    COLOR_GOLD,
    COLOR_HEALTH,
    COLOR_PATH,
    COLOR_PATH_HINT,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_WARNING,
    MAP_ORDER,
    TOWER_BASE_COSTS,
)
from resources import GRAPHICS, load_font


class Renderer:
    def __init__(self, surface: pygame.Surface, game) -> None:
        self.surface = surface
        self.game = game
        self.font = load_font(20)
        self.font_small = load_font(16)
        self.font_big = load_font(32, bold=True)

    def draw(self, game, ui, i18n) -> None:
        surf = self.surface
        surf.fill(COLOR_BG)
        if ui.state == "main_menu":
            self._draw_main_menu(ui, i18n)
        elif ui.state == "campaign":
            self._draw_campaign(ui, i18n)
        elif ui.state == "settings":
            self._draw_settings(ui, i18n)
        elif ui.state == "achievements":
            self._draw_achievements(ui, i18n)
        elif ui.state == "playing":
            self._draw_game(game, i18n)
        elif ui.state == "paused":
            self._draw_game(game, i18n)
            self._draw_pause_overlay(i18n)
        elif ui.state == "results":
            self._draw_results(ui, i18n)

    # ------------------------------------------------------------------ text
    def _draw_text(self, text, x, y, font=None, color=COLOR_TEXT, center=False):
        font = font or self.font
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.surface.blit(surf, rect)
        return rect

    # ---------------------------------------------------------------- menus
    def _draw_main_menu(self, ui, i18n) -> None:
        w, h = self.surface.get_size()
        cx, cy = w // 2, h // 2
        self._draw_text(i18n.t("ui", "title"), cx, cy - 180, self.font_big, COLOR_ACCENT, True)
        btns = ["play", "campaign", "endless", "achievements", "settings", "quit"]
        for i, key in enumerate(btns):
            label = i18n.t("ui", key)
            hover = ui.hover == key
            self._draw_button(cx - 140, cy - 70 + i * 52, 280, 44, label, hover)
        self._draw_text(
            i18n.t("ui", "language") + ": " + i18n.t("ui", f"language_{i18n.language}"),
            20,
            h - 30,
            self.font_small,
            COLOR_TEXT_DIM,
        )

    def _draw_button(self, x, y, w, h, label, hover=False) -> pygame.Rect:
        surf = GRAPHICS.button(w, h, active=True)
        if hover:
            tint = surf.copy()
            tint.fill((255, 255, 255, 26), special_flags=pygame.BLEND_RGBA_ADD)
            surf = tint
        rect = surf.get_rect(topleft=(x, y))
        self.surface.blit(surf, rect)
        self._draw_text(label, x + w // 2, y + h // 2, self.font, COLOR_TEXT, True)
        return rect

    def _draw_campaign(self, ui, i18n) -> None:
        w, h = self.surface.get_size()
        self._draw_text(i18n.t("ui", "campaign"), w // 2, 36, self.font_big, COLOR_ACCENT, True)
        for i, key in enumerate(MAP_ORDER):
            col = i % 3
            row = i // 3
            bx = 100 + col * 390
            by = 110 + row * 210
            unlocked = ui.campaign.is_unlocked(key)
            completed = ui.campaign.is_completed(key)
            stars = ui.campaign.stars_for(key)
            box_color = COLOR_ACCENT if unlocked else COLOR_TEXT_DIM
            rect = pygame.Rect(bx, by, 350, 180)
            pygame.draw.rect(self.surface, (42, 36, 58), rect, border_radius=8)
            pygame.draw.rect(self.surface, box_color, rect, width=2, border_radius=8)
            name = i18n.t("campaign", f"{key}_name")
            desc = i18n.t("campaign", f"{key}_desc")
            self._draw_text(name, bx + 16, by + 14, self.font, COLOR_TEXT)
            self._draw_text(desc, bx + 16, by + 44, self.font_small, COLOR_TEXT_DIM)
            if completed:
                status = f"★{stars}  {i18n.t('ui', 'victory')}"
                scolor = COLOR_GOLD
            elif not unlocked:
                status = (
                    i18n.t("ui", "locked")
                    if "locked" in i18n.t("ui", "")
                    else ("Заблокировано" if i18n.language == "ru" else "Locked")
                )
                scolor = COLOR_WARNING
            else:
                status = i18n.t("ui", "play")
                scolor = COLOR_ACCENT
            self._draw_text(status, bx + 16, by + 144, self.font_small, scolor)

    def _draw_settings(self, ui, i18n) -> None:
        w, h = self.surface.get_size()
        self._draw_text(i18n.t("settings", "title"), w // 2, 36, self.font_big, COLOR_ACCENT, True)
        y = 130
        rows = [
            (i18n.t("settings", "language"), f"{i18n.t('ui', f'language_{ui.settings.language}')}"),
            (i18n.t("settings", "volume"), f"{int(ui.settings.volume * 100)}%"),
            (i18n.t("settings", "fullscreen"), "On" if ui.settings.fullscreen else "Off"),
        ]
        for label, val in rows:
            self._draw_text(label, 120, y, self.font, COLOR_TEXT)
            self._draw_text(val, w - 240, y, self.font, COLOR_ACCENT)
            y += 52
        self._draw_button(w // 2 - 100, h - 80, 200, 44, i18n.t("ui", "back"), False)

    def _draw_achievements(self, ui, i18n) -> None:
        w, h = self.surface.get_size()
        self._draw_text(i18n.t("ui", "achievements"), w // 2, 30, self.font_big, COLOR_ACCENT, True)
        y = 90
        for aid, _data in ACHIEVEMENTS.items():
            done = aid in ui.campaign.achievements
            title = i18n.achievement(aid, "title")
            desc = i18n.achievement(aid, "desc")
            mark = "[X] " if done else "[ ] "
            self._draw_text(mark + title, 100, y, self.font, COLOR_GOLD if done else COLOR_TEXT_DIM)
            self._draw_text(desc, 140, y + 22, self.font_small, COLOR_TEXT_DIM)
            y += 62
            if y > h - 70:
                break
        self._draw_button(w // 2 - 100, h - 55, 200, 44, i18n.t("ui", "back"), False)

    # ---------------------------------------------------------------- game
    def _draw_game(self, game, i18n) -> None:
        self._draw_map(game.map)
        self._draw_enemies(game)
        self._draw_projectiles(game)
        self._draw_explosions(game)
        self._draw_particles(game)
        self._draw_towers(game)
        self._draw_placement_preview(game)
        self._draw_build_palette(game, i18n)
        self._draw_warnings(game)
        self._draw_hud(game, i18n)
        if game.placement_mode:
            self._draw_placement_cursor(game, i18n)

    def _draw_map(self, map_data) -> None:
        surf = self.surface
        ox, oy = self.game.grid_offset
        ts = self.game.tile_size
        for y in range(map_data.rows):
            for x in range(map_data.cols):
                rect = pygame.Rect(ox + x * ts, oy + y * ts, ts, ts)
                if map_data.is_path(x, y):
                    pygame.draw.rect(surf, COLOR_PATH, rect)
                    pygame.draw.rect(surf, COLOR_PATH_HINT, rect, 1)
                elif map_data.is_obstacle(x, y):
                    pygame.draw.rect(surf, (34, 30, 46), rect)
                    pygame.draw.rect(surf, (60, 50, 80), rect, 1)
                else:
                    pygame.draw.rect(surf, COLOR_BG, rect)
                    pygame.draw.rect(surf, (24, 20, 34), rect, 1)
        bx, by = map_data.base_pixel
        pygame.draw.rect(surf, COLOR_DANGER, (bx - 14, by - 14, 28, 28), border_radius=4)
        pygame.draw.rect(surf, COLOR_TEXT, (bx - 14, by - 14, 28, 28), width=2, border_radius=4)

    def _draw_enemies(self, game) -> None:
        surf = self.surface
        for e in game.enemies:
            img = GRAPHICS.enemy(e.enemy_id, size=max(14, e.size), flying=e.flying)
            rect = img.get_rect(center=(int(e.x), int(e.y)))
            surf.blit(img, rect)
            bar_w = 24
            fill = max(0, e.hp / e.max_hp) if e.max_hp > 0 else 0
            pygame.draw.rect(surf, (60, 60, 70), (e.x - bar_w / 2, e.y - e.size - 7, bar_w, 4))
            pygame.draw.rect(surf, COLOR_HEALTH, (e.x - bar_w / 2, e.y - e.size - 7, bar_w * fill, 4))

    def _draw_projectiles(self, game) -> None:
        surf = self.surface
        for p in game.projectiles:
            img = GRAPHICS.projectile(p.data.proj_id)
            rect = img.get_rect(center=(int(p.x), int(p.y)))
            surf.blit(img, rect)

    def _draw_explosions(self, game) -> None:
        surf = self.surface
        for ex in game.explosions:
            frames = GRAPHICS.explosion_frames(6, ex["max_radius"])
            frame = min(5, ex.get("frame", 0))
            img = frames[frame]
            rect = img.get_rect(center=(int(ex["x"]), int(ex["y"])))
            surf.blit(img, rect)

    def _draw_particles(self, game) -> None:
        surf = self.surface
        for p in game.particles:
            color = p.get("color", (255, 255, 255))
            size = int(p.get("size", 4))
            alpha = max(0, min(255, int(255 * p.get("life", 400) / 400)))
            surf2 = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf2, (*color, alpha), (size, size), size)
            surf.blit(surf2, (int(p["x"] - size), int(p["y"] - size)))

    def _draw_towers(self, game) -> None:
        surf = self.surface
        for t in game.towers:
            cx, ty = t.center_pixel(game.tile_size)
            img = GRAPHICS.tower(t.tower_id, size=30)
            rect = img.get_rect(center=(int(cx), int(ty)))
            surf.blit(img, rect)
            if t is game.selected_tower:
                r = int(t.range)
                rc = GRAPHICS.range_circle(r)
                surf.blit(rc, rc.get_rect(center=(int(cx), int(ty))))
                pygame.draw.circle(surf, COLOR_ACCENT, (int(cx), int(ty)), 6, 2)
            self._draw_text(str(t.level), int(cx), int(ty - 16), self.font_small, COLOR_GOLD, True)

    def _draw_placement_preview(self, game) -> None:
        if not game.placement_mode or game.placement_pos is None:
            return
        gx, gy = game.placement_pos
        ox, oy = game.grid_offset
        ts = game.tile_size
        valid = game.map.can_place_tower(gx, gy) if game.map else False
        tile = GRAPHICS.placement_tile(ts, valid)
        self.surface.blit(tile, (ox + gx * ts, oy + gy * ts))

    def _draw_placement_cursor(self, game, i18n) -> None:
        mx, my = pygame.mouse.get_pos()
        name = i18n.tower_display(game.placement_mode, "name")
        cost = TOWER_BASE_COSTS[game.placement_mode]
        self._draw_text(f"{name}  {cost}", mx + 14, my + 14, self.font_small, COLOR_TEXT)
        if game.currency < cost:
            self._draw_text(i18n.t("ui", "cannot_afford"), mx + 14, my + 32, self.font_small, COLOR_DANGER)

    def _draw_build_palette(self, game, i18n) -> None:
        surf = self.surface
        ox, oy = game.grid_offset
        ts = game.tile_size
        # palette bar sits below the grid
        bar_y = oy + game.map.rows * ts + 10
        bar_h = 78
        pygame.draw.rect(surf, (26, 22, 38), (ox, bar_y, game.map.cols * ts, bar_h), border_radius=6)
        pygame.draw.rect(surf, COLOR_ACCENT, (ox, bar_y, game.map.cols * ts, bar_h), width=2, border_radius=6)
        self._draw_text(i18n.t("ui", "place"), ox + 10, bar_y + 6, self.font_small, COLOR_TEXT)
        bx = ox + 110
        by = bar_y + 10
        btn_w = 100
        for i, tower_id in enumerate(["archer", "cannon", "frost", "arc", "poison", "support"]):
            btn_x = bx + i * (btn_w + 10)
            selected = game.placement_mode == tower_id
            cost = TOWER_BASE_COSTS[tower_id]
            affordable = game.currency >= cost
            btn_color = COLOR_ACCENT if selected else (COLOR_TEXT_DIM if not affordable else COLOR_TEXT)
            rect = pygame.Rect(btn_x, by, btn_w - 8, bar_h - 20)
            pygame.draw.rect(surf, (42, 36, 58), rect, border_radius=4)
            pygame.draw.rect(surf, btn_color, rect, width=2 if selected else 1, border_radius=4)
            img = GRAPHICS.tower(tower_id, size=24)
            surf.blit(img, img.get_rect(center=(btn_x + 18, by + 26)))
            name = i18n.tower_display(tower_id, "name")
            self._draw_text(name, btn_x + 40, by + 8, self.font_small, COLOR_TEXT if affordable else COLOR_TEXT_DIM)
            self._draw_text(
                f"{cost}", btn_x + 40, by + 26, self.font_small, COLOR_GOLD if affordable else COLOR_TEXT_DIM
            )
            self._draw_text(str(i + 1), btn_x + btn_w - 24, by + 8, self.font_small, COLOR_ACCENT)

    def _draw_warnings(self, game) -> None:
        surf = self.surface
        w = surf.get_width()
        for wn in game.warnings:
            if wn["kind"] == "boss_arrival":
                self._draw_text("БОСС", w // 2, 80, self.font_big, COLOR_DANGER, True)
            elif wn["kind"] == "ability_warning":
                tx, ty = wn["target"]
                s = wn["ms"] / 700.0
                r = wn["radius"] * (0.5 + 0.5 * s)
                pygame.draw.circle(surf, COLOR_WARNING, (int(tx), int(ty)), int(r), 3)

    # ---------------------------------------------------------------- HUD
    def _draw_hud(self, game, i18n) -> None:
        surf = self.surface
        w, h = surf.get_size()
        pygame.draw.rect(surf, (26, 22, 38), (0, 0, w, 60))
        pygame.draw.line(surf, COLOR_ACCENT, (0, 60), (w, 60), 2)
        self._draw_text(f"{i18n.t('ui', 'currency')}: {game.currency}", 20, 14, self.font, COLOR_GOLD)
        bh_color = COLOR_HEALTH if game.base_health > 50 else COLOR_DANGER
        self._draw_text(
            f"{i18n.t('ui', 'base_health')}: {game.base_health}/{game.base_max_health}",
            230,
            14,
            self.font,
            bh_color,
        )
        wm = game.wave_manager
        if wm.endless:
            wave_txt = f"{i18n.t('ui', 'wave')}: ∞/{wm.endless_wave}"
        else:
            wave_txt = f"{i18n.t('ui', 'wave')}: {wm.wave.index if wm.wave else 0}"
        self._draw_text(wave_txt, w - 320, 14, self.font, COLOR_TEXT)
        rem = sum(1 for e in game.enemies if e.alive)
        self._draw_text(
            f"{i18n.t('ui', 'enemies_remaining')}: {rem}",
            w - 320,
            40,
            self.font_small,
            COLOR_TEXT_DIM,
        )
        self._draw_text(f"x{game.game_speed}", w - 140, 40, self.font_small, COLOR_ACCENT)
        if game.selected_tower:
            self._draw_tower_panel(game.selected_tower, i18n)

    def _draw_tower_panel(self, tower, i18n) -> None:
        surf = self.surface
        w, h = surf.get_size()
        panel_w = 210
        panel_x = w - panel_w - 20
        panel_y = 80
        pygame.draw.rect(surf, (26, 22, 38), (panel_x, panel_y, panel_w, 180), border_radius=6)
        pygame.draw.rect(surf, COLOR_ACCENT, (panel_x, panel_y, panel_w, 180), width=2, border_radius=6)
        name = i18n.tower_display(tower.tower_id, "name")
        self._draw_text(f"{name}  L{tower.level}", panel_x + 12, panel_y + 10, self.font, COLOR_TEXT)
        stats = [
            (i18n.t("ui", "damage"), f"{tower.damage:.0f}"),
            (i18n.t("ui", "range"), f"{tower.range:.0f}"),
            (i18n.t("ui", "speed"), f"{tower.cooldown_ms:.0f}ms"),
        ]
        yy = panel_y + 40
        for label, val in stats:
            self._draw_text(label, panel_x + 12, yy, self.font_small, COLOR_TEXT_DIM)
            self._draw_text(val, panel_x + panel_w - 55, yy, self.font_small, COLOR_ACCENT)
            yy += 22
        self._draw_text("Цель: " + tower.target_mode, panel_x + 12, yy + 6, self.font_small, COLOR_TEXT_DIM)
        yy += 30
        cost = tower.upgrade_cost()
        if cost:
            self._draw_button(panel_x + 12, yy, 95, 30, f"{i18n.t('ui', 'upgrade')} {cost}", False)
        self._draw_button(panel_x + 114, yy, 84, 30, i18n.t("ui", "sell"), False)

    def _draw_pause_overlay(self, i18n) -> None:
        surf = self.surface
        w, h = surf.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))
        self._draw_text(i18n.t("ui", "paused"), w // 2, h // 2 - 30, self.font_big, COLOR_TEXT, True)
        self._draw_button(w // 2 - 90, h // 2 + 30, 180, 40, i18n.t("ui", "resume"), False)

    def _draw_results(self, ui, i18n) -> None:
        surf = self.surface
        w, h = surf.get_size()
        title = i18n.t("ui", "victory") if ui.victory else i18n.t("ui", "defeat")
        color = COLOR_ACCENT if ui.victory else COLOR_DANGER
        self._draw_text(title, w // 2, h // 2 - 70, self.font_big, color, True)
        self._draw_text(f"{i18n.t('ui', 'stars')}: {ui.stars}", w // 2, h // 2 - 15, self.font, COLOR_GOLD, True)
        self._draw_button(w // 2 - 100, h // 2 + 50, 200, 44, i18n.t("ui", "main_menu"), False)
