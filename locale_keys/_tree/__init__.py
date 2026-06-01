"""Auto-generated locale root. Do not edit."""
from __future__ import annotations

from dataclasses import dataclass

from locale_keys._tree.commands import Commands, build_commands
from locale_keys._tree.logs import Logs, build_logs
from locale_keys._tree.admin import Admin, build_admin
from locale_keys._tree.other import build_other

@dataclass(frozen=True, slots=True)
class LocaleRoot:
    commands: Commands
    logs: Logs
    admin: Admin
    ai: Ai
    channel: Channel
    countries: Countries
    delete: Delete
    display: Display
    errors: Errors
    frequency: Frequency
    fun: Fun
    funcmd: Funcmd
    games: Games
    giveaway: Giveaway
    hangman: Hangman
    image: Image
    level: Level
    levelcommands: Levelcommands
    listeners: Listeners
    math: Math
    minigame: Minigame
    minigames: Minigames
    presence: Presence
    setup: Setup
    target: Target
    top: Top
    twitch: Twitch
    utility: Utility
    utilitycmd: Utilitycmd

def build_locale() -> LocaleRoot:
    other = build_other()
    return LocaleRoot(
        commands=build_commands(),
        logs=build_logs(),
        admin=build_admin(),
        ai=other.ai,
        channel=other.channel,
        countries=other.countries,
        delete=other.delete,
        display=other.display,
        errors=other.errors,
        frequency=other.frequency,
        fun=other.fun,
        funcmd=other.funcmd,
        games=other.games,
        giveaway=other.giveaway,
        hangman=other.hangman,
        image=other.image,
        level=other.level,
        levelcommands=other.levelcommands,
        listeners=other.listeners,
        math=other.math,
        minigame=other.minigame,
        minigames=other.minigames,
        presence=other.presence,
        setup=other.setup,
        target=other.target,
        top=other.top,
        twitch=other.twitch,
        utility=other.utility,
        utilitycmd=other.utilitycmd,
    )

locale = build_locale()
