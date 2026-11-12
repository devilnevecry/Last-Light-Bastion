"""UI controller: owns menu state, input handling, and bridges game + renderer."""

from __future__ import annotations


class UI:
    def __init__(self, campaign, settings, i18n) -> None:
        self.campaign = campaign
        self.settings = settings
        self.i18n = i18n
        self.state = "main_menu"  # main_menu, campaign, settings, achievements, playing, paused, results
        self.hover = ""
        self.victory = False
        self.stars = 0
        self.selected_map = None
        self.message = ""
        self.message_ms = 0.0

    # ----- navigation -----
    def to_main_menu(self) -> None:
        self.state = "main_menu"
        self.victory = False
        self.stars = 0

    def to_campaign(self) -> None:
        self.state = "campaign"

    def to_settings(self) -> None:
        self.state = "settings"

    def to_achievements(self) -> None:
        self.state = "achievements"

    def start_map(self, map_key: str, game) -> None:
        if not self.campaign.is_unlocked(map_key):
            return
        self.selected_map = map_key
        game.start_map(map_key)
        self.state = "playing"

    def start_endless(self, game) -> None:
        game.start_map("wastes")  # endless reuses a map; wave manager handles endless
        game.wave_manager.start_endless()
        self.state = "playing"

    def toggle_pause(self) -> None:
        if self.state == "playing":
            self.state = "paused"
        elif self.state == "paused":
            self.state = "playing"
        return self.state == "playing"

    def set_language(self, lang: str) -> None:
        self.i18n.set_language(lang)
        self.settings.language = lang

    # ----- results -----
    def show_results(self, victory: bool, stars: int) -> None:
        self.state = "results"
        self.victory = victory
        self.stars = stars

    # ----- input -----
    def handle_mouse_click(self, pos, game, i18n) -> None:
        x, y = pos
        # handled mostly in main loop per-state; kept as hook
        pass
