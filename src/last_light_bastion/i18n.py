"""Localization manager - centralized translations."""

from __future__ import annotations

from typing import Any

DEFAULT_LANGUAGE = "ru"
SUPPORTED_LANGUAGES = ["ru", "en"]

# All UI strings live here. Keys are dot-namespaced by domain.
TRANSLATIONS: dict[str, dict[str, dict[str, str]]] = {
    "ru": {
        "ui": {
            "title": "Last Light: Bastion",
            "play": "Играть",
            "campaign": "Кампания",
            "endless": "Бесконечный режим",
            "achievements": "Достижения",
            "settings": "Настройки",
            "quit": "Выход",
            "resume": "Продолжить",
            "restart": "Перезапуск",
            "main_menu": "Главное меню",
            "language": "Язык",
            "language_ru": "Русский",
            "language_en": "Английский",
            "game_speed": "Скорость игры",
            "volume": "Громкость",
            "fullscreen": "Полноэкранный режим",
            "back": "Назад",
            "confirm": "Подтвердить",
            "cancel": "Отмена",
            "next_wave": "Следующая волна",
            "start_wave": "Начать волну",
            "wave": "Волна",
            "currency": "Ресурсы",
            "base_health": "Здоровье базы",
            "enemies_remaining": "Врагов осталось",
            "selected": "Выбрано",
            "upgrade": "Улучшить",
            "sell": "Продать",
            "range": "Дальность",
            "damage": "Урон",
            "speed": "Скорость атаки",
            "level": "Уровень",
            "cost": "Стоимость",
            "place": "Построить",
            "cannot_afford": "Недостаточно ресурсов",
            "invalid_placement": "Невозможно построить здесь",
            "paused": "Пауза",
            "victory": "Победа",
            "defeat": "Поражение",
            "stars": "Звёзды",
            "reward": "Награда",
            "continue": "Продолжить",
            "tutorial": "Обучение",
            "help": "Помощь",
        },
        "towers": {
            "archer": {"name": "Лучницкая башня", "desc": "Дешёвая, быстрая однолучная стрельба."},
            "cannon": {"name": "Пушечная башня", "desc": "Медленный, мощный урон по области."},
            "frost": {"name": "Ледяная башня", "desc": "Замедляет врагов в зоне поражения."},
            "arc": {"name": "Разрядная башня", "desc": "Урон перепрыгивает между целями."},
            "poison": {"name": "Ядовитая башня", "desc": "Наносит урон с течением времени."},
            "support": {"name": "Оплот", "desc": "Усиливает соседние башни."},
        },
        "enemies": {
            "basic": {"name": "Базовый", "desc": "Обычный 앞 линий атакующий."},
            "fast": {"name": "Быстрый", "desc": "Быстрый и хрупкий; мчится к Бастиону."},
            "armored": {"name": "Бронированный", "desc": "Толстая броня снижает физический урон."},
            "heavy": {"name": "Тяжёлый", "desc": "Медленный, но невероятно прочный."},
            "flying": {"name": "Летающий", "desc": "Перемещается над местностью; целится только прицелом."},
            "regenerating": {"name": "Регенерирующий", "desc": "Медленно восстанавливает здоровье."},
            "elite": {"name": "Элитный", "desc": "Сбалансированный, прочный и прибыльный."},
        },
        "bosses": {
            "void_reaver": {"name": "Пожиратель пустоты", "desc": "Телепортируется и стреляет пустотой."},
            "flame_titan": {"name": "Пламенный титан", "desc": "Выпускает волны огня и угли."},
            "storm_colossus": {"name": "Колосс шторма", "desc": "Цепной молнии и порывы ветра."},
        },
        "campaign": {
            "wastes": {"name": "Пустоши", "desc": "Введение в защиту Бастиона."},
            "spire": {"name": "Шпиль", "desc": "Летающие враги появляются над шпилем."},
            "delta": {"name": "Дельта", "desc": "Ветвящиеся маршруты требуют разделенной обороны."},
            "rift": {"name": "Разлом", "desc": "Два маршрута одновременно."},
            "bastion": {"name": "Бастион", "desc": "Финальный рубеж с удвоенными путями."},
        },
        "achievements": {
            "first_blood": {"title": "Первая кровь", "desc": "Уничтожь первого врага."},
            "tower_builder": {"title": "Строитель башен", "desc": "Построй любую башню."},
            "master_builder": {"title": "Мастер строительства", "desc": "Построй 10 башен за одно прохождение карты."},
            "full_upgrade": {"title": "Максимальное улучшение", "desc": "Улучшите башню до 3 уровня."},
            "wave_survivor": {"title": "Выживший", "desc": "Пройдите 10 волн."},
            "boss_slayer": {"title": "Победитель босса", "desc": "Победите первого босса."},
            "perfect_defense": {"title": "Идеальная защита", "desc": "Завершите миссию, не потеряв здоровье базы."},
            "all_towers": {"title": "Арсенал", "desc": "Постройте каждый тип башни хотя бы раз."},
            "endless_warrior": {"title": "Вечный воин", "desc": "Достигните 30-й волны в бесконечном режиме."},
            "campaign_conqueror": {"title": "Завоеватель кампании", "desc": "Пройдите все 5 карт кампании."},
            "wealthy": {"title": "Богач", "desc": "Накопите 500 ресурсов одновременно."},
            "flying_counter": {"title": "Сокрушитель потолка", "desc": "Уничтожьте 20 летающих врагов."},
        },
        "objectives": {
            "survive": "Выдержите волны врагов, защищая сердце Бастиона.",
            "defeat_boss": "Победите босса волны, чтобы завершить миссию.",
        },
        "settings": {
            "title": "Настройки",
            "language": "Язык интерфейса",
            "volume": "Громкость звука",
            "fullscreen": "Полноэкранный режим",
        },
        "tutorial": {
            "welcome": "Добро пожаловать в Last Light: Bastion.",
            "build": "Нажмите на выделенную зону, чтобы построить башню.",
            "upgrade": "Выберите башню, чтобы улучшить или продать её.",
            "wave": 'Нажмите "Следующая волна", когда будете готовы.',
            "goal": "Защитите сердце Бастиона от волн врагов.",
        },
    },
    "en": {
        "ui": {
            "title": "Last Light: Bastion",
            "play": "Play",
            "campaign": "Campaign",
            "endless": "Endless Mode",
            "achievements": "Achievements",
            "settings": "Settings",
            "quit": "Quit",
            "resume": "Resume",
            "restart": "Restart",
            "main_menu": "Main Menu",
            "language": "Language",
            "language_ru": "Russian",
            "language_en": "English",
            "game_speed": "Game Speed",
            "volume": "Volume",
            "fullscreen": "Fullscreen",
            "back": "Back",
            "confirm": "Confirm",
            "cancel": "Cancel",
            "next_wave": "Next Wave",
            "start_wave": "Start Wave",
            "wave": "Wave",
            "currency": "Resources",
            "base_health": "Base Health",
            "enemies_remaining": "Enemies Remaining",
            "selected": "Selected",
            "upgrade": "Upgrade",
            "sell": "Sell",
            "range": "Range",
            "damage": "Damage",
            "speed": "Attack Speed",
            "level": "Level",
            "cost": "Cost",
            "place": "Build",
            "cannot_afford": "Not enough resources",
            "invalid_placement": "Cannot build here",
            "paused": "Paused",
            "victory": "Victory",
            "defeat": "Defeat",
            "stars": "Stars",
            "reward": "Reward",
            "continue": "Continue",
            "tutorial": "Tutorial",
            "help": "Help",
        },
        "towers": {
            "archer": {"name": "Archer Tower", "desc": "Inexpensive, fast single-target fire."},
            "cannon": {"name": "Cannon Tower", "desc": "Slow, powerful area damage."},
            "frost": {"name": "Frost Tower", "desc": "Slows enemies in its area."},
            "arc": {"name": "Arc Tower", "desc": "Damage chains between targets."},
            "poison": {"name": "Poison Tower", "desc": "Damage over time."},
            "support": {"name": "Support Tower", "desc": "Boosts nearby towers."},
        },
        "enemies": {
            "basic": {"name": "Basic", "desc": "Standard frontline attacker."},
            "fast": {"name": "Fast", "desc": "Swift and fragile; rushes the Bastion."},
            "armored": {"name": "Armored", "desc": "Thick plating reduces physical damage."},
            "heavy": {"name": "Heavy", "desc": "Slow but extremely durable."},
            "flying": {"name": "Flying", "desc": "Moves over terrain; only ranged towers target."},
            "regenerating": {"name": "Regenerating", "desc": "Slowly restores health over time."},
            "elite": {"name": "Elite", "desc": "Balanced, tough, and rewarding."},
        },
        "bosses": {
            "void_reaver": {"name": "Void Reaver", "desc": "Teleports and fires void bolts."},
            "flame_titan": {"name": "Flame Titan", "desc": "Releases fire waves and embers."},
            "storm_colossus": {"name": "Storm Colossus", "desc": "Chain lightning and gale pushes."},
        },
        "campaign": {
            "wastes": {"name": "The Wastes", "desc": "Introduction to the Bastion's defense."},
            "spire": {"name": "The Spire", "desc": "Flying enemies appear above the spire."},
            "delta": {"name": "The Delta", "desc": "Branching routes require split defense."},
            "rift": {"name": "The Rift", "desc": "Two simultaneous routes."},
            "bastion": {"name": "The Bastion", "desc": "Final line with doubled paths."},
        },
        "achievements": {
            "first_blood": {"title": "First Blood", "desc": "Destroy your first enemy."},
            "tower_builder": {"title": "Tower Builder", "desc": "Build your first tower."},
            "master_builder": {"title": "Master Builder", "desc": "Build 10 towers in a single map run."},
            "full_upgrade": {"title": "Full Upgrade", "desc": "Upgrade a tower to level 3."},
            "wave_survivor": {"title": "Wave Survivor", "desc": "Survive 10 waves."},
            "boss_slayer": {"title": "Boss Slayer", "desc": "Defeat your first boss."},
            "perfect_defense": {"title": "Perfect Defense", "desc": "Complete a mission without losing base health."},
            "all_towers": {"title": "Arsenal", "desc": "Build every tower type at least once."},
            "endless_warrior": {"title": "Endless Warrior", "desc": "Reach wave 30 in Endless mode."},
            "campaign_conqueror": {"title": "Campaign Conqueror", "desc": "Complete all 5 campaign maps."},
            "wealthy": {"title": "Wealthy", "desc": "Hold 500 resources at once."},
            "flying_counter": {"title": "Ceiling Breaker", "desc": "Destroy 20 flying enemies."},
        },
        "objectives": {
            "survive": "Survive enemy waves while defending the Bastion's core.",
            "defeat_boss": "Defeat the boss wave to complete the mission.",
        },
        "settings": {
            "title": "Settings",
            "language": "Interface language",
            "volume": "Sound volume",
            "fullscreen": "Fullscreen mode",
        },
        "tutorial": {
            "welcome": "Welcome to Last Light: Bastion.",
            "build": "Click a highlighted zone to build a tower.",
            "upgrade": "Select a tower to upgrade or sell it.",
            "wave": 'Press "Next Wave" when ready.',
            "goal": "Protect the Bastion's core from enemy waves.",
        },
    },
}

MISSING = "<<MISSING>>"


class I18n:
    """Centralized localization accessor. Language switches at runtime."""

    def __init__(self, language: str = DEFAULT_LANGUAGE) -> None:
        self.language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

    def set_language(self, language: str) -> None:
        if language in SUPPORTED_LANGUAGES:
            self.language = language

    def t(self, domain: str, key: str, **kwargs: Any) -> str:
        strings = TRANSLATIONS.get(self.language, TRANSLATIONS[DEFAULT_LANGUAGE])
        domain_strings = strings.get(domain, {})
        value = domain_strings.get(key)
        if value is None:
            # fall back to default language
            default_domain = TRANSLATIONS[DEFAULT_LANGUAGE].get(domain, {})
            value = default_domain.get(key, MISSING)
        if kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                return value
        return value

    def tower_name(self, tower_id: str) -> str:
        return self.tower_display(tower_id, "name")

    def tower_display(self, tower_id: str, field: str) -> str:
        value = self._nested("towers", tower_id, field)
        if value == MISSING:
            value = tower_id.replace("_", " ").title()
        return value

    def enemy_display(self, enemy_id: str, field: str) -> str:
        value = self._nested("enemies", enemy_id, field)
        if value == MISSING:
            value = enemy_id.replace("_", " ").title()
        return value

    def boss_display(self, boss_id: str, field: str) -> str:
        value = self._nested("bosses", boss_id, field)
        if value == MISSING:
            value = boss_id.replace("_", " ").title()
        return value

    def achievement(self, aid: str, field: str) -> str:
        return self._nested("achievements", aid, field)

    def _nested(self, domain: str, sub: str, field: str) -> str:
        strings = TRANSLATIONS.get(self.language, TRANSLATIONS[DEFAULT_LANGUAGE])
        entry = strings.get(domain, {}).get(sub, {})
        value = entry.get(field)
        if value is None or value == MISSING:
            default_entry = TRANSLATIONS[DEFAULT_LANGUAGE].get(domain, {}).get(sub, {})
            value = default_entry.get(field)
        if value is None:
            value = MISSING
        return value
