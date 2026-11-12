"""Tests for localization: completeness, language switching, Cyrillic."""

from __future__ import annotations

from base import *  # noqa: F403
from i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, TRANSLATIONS, I18n


def test_supported_languages():
    assert "ru" in SUPPORTED_LANGUAGES
    assert "en" in SUPPORTED_LANGUAGES


def test_default_is_russian():
    assert DEFAULT_LANGUAGE == "ru"


def test_translation_lookup_ru():
    i18n = I18n("ru")
    assert i18n.t("ui", "title") == "Last Light: Bastion"
    assert i18n.t("ui", "play") == "Играть"


def test_translation_lookup_en():
    i18n = I18n("en")
    assert i18n.t("ui", "play") == "Play"
    assert i18n.t("ui", "title") == "Last Light: Bastion"


def test_language_switch_no_restart():
    i18n = I18n("ru")
    ru_title = i18n.t("ui", "play")
    i18n.set_language("en")
    en_title = i18n.t("ui", "play")
    assert ru_title != en_title
    assert i18n.language == "en"


def test_tower_and_enemy_descriptions_translated():
    for lang in ["ru", "en"]:
        i18n = I18n(lang)
        for tid in ["archer", "cannon", "frost", "arc", "poison", "support"]:
            name = i18n.tower_display(tid, "name")
            desc = i18n.tower_display(tid, "desc")
            assert name and "<<MISSING" not in name
            assert desc and "<<MISSING" not in desc
        for eid in ["basic", "fast", "armored", "heavy", "flying", "regenerating", "elite"]:
            name = i18n.enemy_display(eid, "name")
            assert name and "<<MISSING" not in name


def test_achievements_translated():
    for lang in ["ru", "en"]:
        i18n = I18n(lang)
        for aid in ["first_blood", "boss_slayer", "campaign_conqueror"]:
            title = i18n.achievement(aid, "title")
            desc = i18n.achievement(aid, "desc")
            assert title and "<<MISSING" not in title
            assert desc and "<<MISSING" not in desc


def test_no_missing_ui_strings():
    for lang in ["ru", "en"]:
        I18n(lang)
        for domain, strings in TRANSLATIONS[lang].items():
            for key, val in strings.items():
                assert "<<MISSING" not in val, f"missing {lang}.{domain}.{key}"
