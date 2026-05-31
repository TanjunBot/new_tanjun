#!/usr/bin/env python3
"""Enrich Crowdin locale entries with accurate context, labels, and max_length."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

LOCALE_DIR = Path(__file__).resolve().parent.parent / "locales"
LOCALES = [
    "en",
    "de",
    "ko",
    "bg",
    "cs",
    "da",
    "el",
    "es-419",
    "fi",
    "fr",
    "hi",
    "hr",
    "hu",
    "id",
    "it",
    "ja",
    "lt",
    "nl",
    "vi",
    "zh-CN",
    "zh-TW",
]

STRIP_LABELS = frozenset({"de.json", "en.json", "unassigned", ""})
STANDARD_FIELDS = frozenset({
    "title",
    "description",
    "name",
    "label",
    "placeholder",
    "true",
    "false",
    "footer",
    "content",
    "author",
})

CAMEL_BOUNDARY = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
LOCALIZE_RE = re.compile(
    r'(?:tanjunLocalizer|localizer)\.localize\(\s*(?:str\([^)]+\)|[^,]+),\s*["\']([^"\']+)["\']'
)
LOCALE_STR_RE = re.compile(r'locale_str\(\s*["\']([^"\']+)["\']')
TITLE_KEY_RE = re.compile(r'["\'](commands\.[^"\']+)["\']')

STRUCTURAL_SEGMENTS = frozenset({
    "select",
    "modal",
    "modals",
    "buttons",
    "button",
    "params",
    "configure",
    "config",
    "wizard",
    "embed",
    "fields",
    "options",
    "choices",
    "channel",
    "user",
    "member",
    "role",
    "message",
    "messages",
    "logs",
    "blacklist",
    "giveaway",
    "battlelog",
    "brawlers",
    "playerinfo",
    "club",
    "help",
    "administration",
    "reports",
    "farewell",
    "welcome",
    "media",
    "trigger",
    "warn",
    "level",
    "rank",
    "leaderboard",
    "add",
    "get",
    "remove",
    "set",
    "ch",
    "w",
    "ds",
    "edit",
    "end",
    "start",
    "list",
    "see",
    "cancel",
    "action",
    "copymembers",
    "above",
    "below",
})

COMMAND_GROUPS = frozenset({
    "admin",
    "utility",
    "fun",
    "level",
    "giveaway",
    "math",
    "ai",
    "games",
    "logs",
    "help",
    "channel",
    "moderation",
    "setup",
    "image",
    "minigame",
    "economy",
    "music",
})

RESULT_KEY_HINTS: dict[str, str] = {
    "forbidden": "the bot lacks Discord permissions (discord.Forbidden)",
    "http_error": "the Discord API returns an HTTP error (uses $status)",
    "notfound": "a required Discord resource was not found (discord.NotFound)",
    "missingpermission": "the user who ran the command lacks the required permission",
    "missingpermissionbot": "the bot lacks the required permission in this server",
    "missingbotpermission": "the bot lacks a required permission",
    "missingpermissions": "required permissions are missing",
    "missingpermissionsbot": "the bot is missing required permissions",
    "missingchannel": "the configured channel does not exist or is inaccessible",
    "missingname": "a required name was not provided",
    "missingtitle": "a required title was not provided",
    "missingpro": "Tanjun Pro is required but not active",
    "no_pro": "Tanjun Pro is required",
    "notplus": "Tanjun Plus is required",
    "no_plus": "Tanjun Plus is required",
    "prorequired": "Tanjun Pro subscription is required",
    "pro_required": "Tanjun Pro subscription is required",
    "success": "the command completed successfully",
    "error": "the command failed with a generic error",
    "failure": "the operation failed",
    "failed": "the operation failed",
    "cancelled": "the user cancelled the flow",
    "timeout": "a select menu or interaction timed out",
    "confirm": "the bot asks the user to confirm an action",
    "forbiddenerror": "the bot cannot perform the action due to permissions",
    "targettoohigh": "the target member's highest role is above the executor's role",
    "roletoohigh": "the target role is higher than the executor may manage",
    "roletoohighbot": "the target role is higher than the bot's highest role",
    "alreadyhasrole": "the member already has that role",
    "doesnothaverole": "the member does not have that role",
    "norole": "no role was selected or found",
    "nouser": "no user was selected or found",
    "usernotfound": "the user was not found",
    "notfound": "the resource was not found",
    "notset": "a required setting has not been configured yet",
    "alreadyset": "this setting is already configured",
    "alreadyexists": "this entry already exists",
    "alreadyexists": "duplicate entry",
    "invalidcolor": "the color value is invalid",
    "invalidicon": "the role icon file type is invalid",
    "icontoolarge": "the role icon file is too large",
    "nametoolong": "the name exceeds Discord's length limit",
    "reasontoolong": "the reason text is too long",
    "invalidamount": "the amount is invalid",
    "invalidduration": "the duration is invalid",
    "invalidinput": "the user input is invalid",
    "invalid_level": "the level number is invalid",
    "invalid_color": "the color is invalid",
    "cooldown": "the command is on cooldown",
    "blacklisted": "the user or item is blacklisted",
    "notblacklisted": "the user is not on the blacklist",
    "alreadyblacklisted": "already on the blacklist",
    "blocked": "the user is blocked",
    "notblocked": "the user is not blocked",
    "notlocked": "the channel is not locked",
    "alreadylocked": "the channel is already locked",
    "nottimedout": "the member is not timed out",
    "alreadytimedout": "the member is already timed out",
    "no_messages": "no messages matched the criteria",
    "noparticipants": "there are no giveaway participants",
    "notended": "the giveaway has not ended yet",
    "alreadyended": "the giveaway has already ended",
    "endedgiveaway": "the giveaway has ended",
    "participation_success": "the user successfully entered the giveaway",
    "participation_removed": "the user was removed from the giveaway",
    "givenup": "the player gave up the minigame",
    "notyourgame": "the interaction is not for this user's game",
    "guildonly": "the command must be used in a server",
    "no_permission": "the user lacks permission",
    "no_read_perms": "the bot cannot read the channel",
    "no_send_perms": "the bot cannot send messages in the channel",
    "no_view_perms": "the bot cannot view the channel",
    "no_message_delete_perms": "the bot cannot delete messages",
    "no_moderate_members_perms": "the bot cannot moderate members",
    "deletesuccess": "deletion succeeded",
    "removed": "removal succeeded",
    "disabled": "the feature is disabled",
    "enabled": "the feature was enabled",
    "already_disabled": "already disabled",
    "already_enabled": "already enabled",
    "select": "a select menu prompt",
    "modal": "a modal dialog",
    "initial": "initial wizard or setup step",
    "input": "user input step",
    "show": "display or list view",
    "configure": "configuration wizard step",
    "completed": "operation completed (admin sync, etc.)",
    "added": "item was added",
    "blocked": "user was blocked",
    "unexpected_error": "an unexpected error occurred",
    "cooldown": "command cooldown active",
    "validation": "input validation failed",
    "permission": "permission check failed",
    "interaction": "interaction handling error",
    "transformer_error": "Discord could not parse a command option",
    "already_afk": "the user is already AFK",
    "opted_out": "the user opted out of a feature",
    "notlinked": "account is not linked",
    "alreadylinked": "account is already linked",
    "roleiconsnotenabled": "the server does not have the role icons feature",
    "managedrole": "the role is managed by an integration and cannot be edited",
    "partialsuccess": "the operation only partially succeeded",
    "multipleprompt": "prompt when multiple items were selected",
    "multipleprompt": "prompt for multiple selection",
    "noselection": "nothing was selected",
    "multiplesuccess": "success message for bulk operation",
}


@dataclass
class ParsedKey:
    parts: list[str]
    field: str | None = None
    subfield: str | None = None
    result_key: str | None = None
    param_name: str | None = None
    is_params: bool = False
    is_plain: bool = False
    plain_text: str = ""
    kind: str = "generic"


def humanize_token(token: str) -> str:
    token = token.replace("_", " ").replace("-", " ")
    token = CAMEL_BOUNDARY.sub(" ", token)
    return " ".join(token.split())


def normalize_key(key: str) -> str:
    return key.replace("_", ".")


def _looks_like_result_key(segment: str, cmd_tail: list[str], *, root: str | None = None) -> bool:
    if root == "errors" and len(cmd_tail) <= 2:
        return False
    if segment.lower() in STRUCTURAL_SEGMENTS:
        return False
    seg = segment.lower()
    if seg in RESULT_KEY_HINTS:
        return True
    if seg in COMMAND_GROUPS:
        return False
    if len(cmd_tail) < 2:
        return False
    if CAMEL_BOUNDARY.search(segment):
        return True
    if "_" in segment and seg in RESULT_KEY_HINTS:
        return True
    return False


def parse_identifier(identifier: str) -> ParsedKey:
    if "." not in identifier:
        return ParsedKey(parts=[], is_plain=True, plain_text=identifier, kind="plain")

    parts = identifier.split(".")
    lower = [p.lower() for p in parts]

    if "params" in lower:
        idx = lower.index("params")
        param_name = parts[idx + 1] if idx + 1 < len(parts) else ""
        found_field = parts[-1].lower() if parts[-1].lower() in STANDARD_FIELDS else None
        return ParsedKey(
            parts=parts,
            field=found_field,
            param_name=param_name,
            is_params=True,
            kind="slash_option",
        )

    field: str | None = None
    subfield: str | None = None
    work = list(parts)

    if len(work) >= 2 and work[-2].lower() == "description" and work[-1].lower() not in STANDARD_FIELDS:
        field = "description"
        subfield = work[-1]
        work = work[:-2]
    elif work[-1].lower() in STANDARD_FIELDS:
        field = work[-1].lower()
        work = work[:-1]

    result_key: str | None = None
    if field and work:
        root = work[0]
        if work[0] == "commands" and len(work) >= 3:
            tail = work[1:]
            if _looks_like_result_key(tail[-1], tail, root=root):
                result_key = tail[-1]
                work = [work[0], *tail[:-1]]
        elif work[0] != "commands" and len(work) >= 2 and field in {"title", "description"}:
            tail = work
            if _looks_like_result_key(tail[-1], tail, root=root):
                result_key = tail[-1]
                work = tail[:-1]

    pk = ParsedKey(parts=work, field=field, subfield=subfield, result_key=result_key)

    if not work:
        pk.kind = "leaf"
        return pk
    if work[0] == "commands":
        pk.kind = "commands"
    elif work[0] == "admin":
        pk.kind = "slash_command"
    elif work[0] == "errors":
        pk.kind = "errors"
    elif work[0] == "listeners":
        pk.kind = "listeners"
    elif work[0] == "logs":
        pk.kind = "logs"
    elif work[0] == "minigames":
        pk.kind = "minigames"
    elif work[0] == "level":
        pk.kind = "level"
    elif work[0] == "countries":
        pk.kind = "countries"
    elif work[0] == "channel":
        pk.kind = "channel"
    elif work[0] == "fun":
        pk.kind = "fun"
    elif work[0] == "ai":
        pk.kind = "ai"
    else:
        pk.kind = "generic"
    return pk


def slash_ref(pk: ParsedKey) -> str:
    parts = pk.parts
    if not parts:
        return "this command"
    if parts[0] == "commands" and len(parts) >= 2:
        if parts[1] == "help":
            rest = parts[2:]
            base = "`/help`"
            if rest and rest != ["select"]:
                return f"{base} ({humanize_token(' '.join(rest))})"
            return base
        if len(parts) >= 3:
            group, sub = parts[1], parts[2]
            rest = parts[3:]
            base = f"`/{group} {sub}`" if group != sub else f"`/{sub}`"
            if rest:
                nested = humanize_token(" ".join(rest))
                return f"{base} ({nested})"
            return base
        return f"`/{parts[1]}`"
    if parts[0] == "channel" and len(parts) >= 2:
        rest = humanize_token(" ".join(parts[1:]))
        return f"`/channel` ({rest})"
    if parts[0] == "admin" and len(parts) >= 2:
        return f"`/{parts[1]}`"
    if len(parts) >= 2:
        return f"`/{parts[0]} {parts[1]}`"
    return f"`/{parts[0]}`"


def result_meaning(result_key: str) -> str:
    key = result_key.lower().replace("_", "")
    if result_key.lower() in RESULT_KEY_HINTS:
        return RESULT_KEY_HINTS[result_key.lower()]
    compact = result_key.lower()
    if compact in RESULT_KEY_HINTS:
        return RESULT_KEY_HINTS[compact]
    return humanize_token(result_key)


def field_phrase(field: str | None, subfield: str | None) -> str:
    if field == "title":
        return "Title"
    if field == "description" and subfield:
        return f"Body text for the embed field `{subfield}`"
    if field == "description":
        return "Description body"
    if field == "name":
        return "Name"
    if field == "label":
        return "Label"
    if field == "placeholder":
        return "Placeholder text"
    if field in {"true", "false"}:
        return f"Choice label for option value `{field}`"
    return "Text"


def build_code_index(project_root: Path) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "build", "node_modules", "locales", "tests"}]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            try:
                text = Path(path).read_text(encoding="utf-8")
            except OSError:
                continue
            rel = os.path.relpath(path, project_root)
            for pattern in (LOCALIZE_RE, LOCALE_STR_RE, TITLE_KEY_RE):
                for match in pattern.finditer(text):
                    raw = match.group(1)
                    key = normalize_key(raw)
                    index.setdefault(key, set()).add(rel)
                    if "_" in raw:
                        index.setdefault(raw.replace("_", "."), set()).add(rel)
    return index


def code_hint(identifier: str, code_index: dict[str, set[str]]) -> str:
    paths = code_index.get(identifier) or code_index.get(identifier.replace(".", "_"))
    if not paths:
        return ""
    rel = sorted(paths)[0]
    return f" Used in `{rel}`."


def infer_context(
    identifier: str,
    source_string: str,
    pk: ParsedKey,
    code_index: dict[str, set[str]],
) -> str:
    hint = code_hint(identifier, code_index)
    src_preview = source_string.replace("\n", " ").strip()
    if len(src_preview) > 120:
        src_preview = src_preview[:117] + "…"

    if pk.is_plain:
        return (
            f"Discord slash command category or command name shown in the command browser "
            f'(identifier is the legacy English label). English source: "{src_preview}".{hint}'
        )

    if pk.is_params:
        cmd = slash_ref(pk)
        opt = pk.param_name or "option"
        if pk.field == "name":
            return (
                f"Display name of the `{opt}` option on {cmd} "
                f"(shown in Discord's slash command option list).{hint}"
            )
        if pk.field == "description":
            return (
                f"Help text describing the `{opt}` option on {cmd} "
                f"(shown when the user focuses that option).{hint}"
            )
        if pk.field in {"true", "false"}:
            return f"Label for the `{pk.field}` choice of a boolean `{opt}` option on {cmd}.{hint}"
        return f"Option text for `{opt}` on {cmd}.{hint}"

    cmd = slash_ref(pk)

    if pk.kind == "slash_command":
        sub = pk.parts[1] if len(pk.parts) > 1 else "command"
        if pk.field == "name":
            return (
                f"Slash command name for {cmd} (lowercase, no spaces; registered via locale_str). "
                f"Discord shows this in the command list.{hint}"
            )
        if pk.field == "description":
            return (
                f"Short description of {cmd} in Discord's slash command browser "
                f"(max ~100 characters).{hint}"
            )
        return f"Registration string for {cmd} ({humanize_token(pk.parts[-1])}).{hint}"

    if pk.kind == "errors":
        topic = humanize_token(pk.parts[1]) if len(pk.parts) > 1 else "general"
        if pk.field == "title":
            return f"Title of the global {topic} error embed (shown by the error handler, not one command).{hint}"
        if pk.field == "description":
            return (
                f"Description of the global {topic} error embed. "
                f'May use $variables. English: "{src_preview}".{hint}'
            )
        return f"Global error copy for {topic}.{hint}"

    if pk.kind == "listeners":
        event = humanize_token(".".join(pk.parts[1:])) if len(pk.parts) > 1 else "event"
        return (
            f"Message shown by an event listener ({event}). "
            f'English: "{src_preview}".{hint}'
        )

    if pk.kind == "logs":
        topic = humanize_token(".".join(pk.parts[1:]))
        if pk.field == "title":
            return f"Title for a server logging / audit-log UI related to {topic}.{hint}"
        if pk.field == "description":
            return f"Description for a server logging / audit-log UI related to {topic}.{hint}"
        return f"Logging feature copy: {topic}.{hint}"

    if pk.kind == "minigames":
        topic = humanize_token(".".join(pk.parts[1:]))
        if pk.field == "name":
            return f"Minigame mode or option name: {topic}.{hint}"
        return f"Minigame UI copy ({topic}). English: \"{src_preview}\".{hint}"

    if pk.kind == "level":
        topic = humanize_token(".".join(pk.parts[1:]))
        if pk.result_key:
            meaning = result_meaning(pk.result_key)
            fp = field_phrase(pk.field, pk.subfield)
            return f"{fp} shown for the leveling command {cmd} when {meaning}.{hint}"
        if pk.field == "name":
            return f"Leveling slash command or subcommand name: {topic}.{hint}"
        if pk.field == "description":
            return f"Leveling slash command description: {topic}.{hint}"
        return f"Leveling system text ({topic}).{hint}"

    if pk.kind == "fun":
        if len(pk.parts) >= 4 and pk.parts[1] == "action" and pk.parts[2] == "choice":
            action = pk.parts[3]
            return (
                f"Choice label for the `{action}` action in the `/fun action` slash command "
                f"(user picks an interaction type).{hint}"
            )
        topic = humanize_token(".".join(pk.parts[1:]))
        return f"Fun command UI text ({topic}). English: \"{src_preview}\".{hint}"

    if pk.kind == "ai":
        topic = humanize_token(".".join(pk.parts))
        return f"AI / ChatGPT command parameter or UI label ({topic}). English: \"{src_preview}\".{hint}"

    if pk.kind == "countries":
        return (
            f"Country or region name displayed in a selector "
            f"({humanize_token(pk.parts[-1])}).{hint}"
        )

    if pk.kind == "channel":
        cmd = slash_ref(pk)
        if pk.is_params:
            opt = pk.param_name or "option"
            if pk.field == "name":
                return f"Option name `{opt}` on {cmd}.{hint}"
            if pk.field == "description":
                return f"Option description for `{opt}` on {cmd}.{hint}"
        if pk.field == "name":
            return f"Slash command or subcommand name for {cmd} (locale_str registration).{hint}"
        if pk.field == "description":
            return f"Slash command description for {cmd} shown in Discord's command browser.{hint}"
        if pk.field == "label":
            return f"Button or action label for {cmd}.{hint}"
        topic = humanize_token(".".join(pk.parts[1:]))
        return f"Channel management command text for {cmd} ({topic}).{hint}"

    if pk.kind == "commands":
        if pk.result_key and pk.field:
            meaning = result_meaning(pk.result_key)
            fp = field_phrase(pk.field, pk.subfield)
            if meaning in RESULT_KEY_HINTS.values() or pk.result_key.lower() in RESULT_KEY_HINTS:
                return f"{fp} of the reply embed for {cmd} when {meaning}.{hint}"
            return f"{fp} of the reply embed for {cmd} ({meaning}).{hint}"

        if pk.field == "name":
            return f"Slash subcommand or option name for {cmd}.{hint}"
        if pk.field == "description" and pk.subfield:
            return (
                f"Text for embed field `{pk.subfield}` in a {cmd} response. "
                f'English: "{src_preview}".{hint}'
            )
        if pk.field == "description":
            return (
                f"Description text for {cmd} (response embed or command help). "
                f'English: "{src_preview}".{hint}'
            )
        if pk.field == "title":
            return f"Title of a reply embed for {cmd}.{hint}"
        if pk.field == "label":
            return f"Button or component label on {cmd}.{hint}"
        if pk.field == "placeholder":
            return (
                f"Placeholder text inside a Discord select menu on {cmd} "
                f"(grey hint before the user chooses an option).{hint}"
            )
        if pk.field == "description" and pk.subfield:
            return (
                f"Value for the `{pk.subfield}` field inside a {cmd} reply embed. "
                f'English: "{src_preview}".{hint}'
            )

        leaf = pk.parts[-1] if pk.parts else identifier
        parent = ParsedKey(parts=pk.parts[:-1], kind=pk.kind)
        parent_cmd = slash_ref(parent)
        return (
            f"User-visible message for {parent_cmd} ({humanize_token(leaf)}). "
            f'English: "{src_preview}".{hint}'
        )

    if pk.result_key and pk.field:
        meaning = result_meaning(pk.result_key)
        fp = field_phrase(pk.field, pk.subfield)
        return f"{fp} for {cmd} when {meaning}.{hint}"

    if pk.field == "title":
        return f"Embed or dialog title ({humanize_token('.'.join(pk.parts))}).{hint}"
    if pk.field == "description":
        return f"Embed or dialog description ({humanize_token('.'.join(pk.parts))}).{hint}"
    if pk.field == "name":
        return f"Display name ({humanize_token('.'.join(pk.parts))}).{hint}"

    topic = humanize_token(".".join(pk.parts))
    if len(pk.parts) == 1 and pk.parts[0] in {"display", "delete", "target", "top", "presence", "frequency", "twitch"}:
        return (
            f"Slash command option registration key for `{identifier}` "
            f"(maps to locale_str in command definitions). English: \"{src_preview}\".{hint}"
        )
    if "penalty" in identifier or "top.p" in identifier or identifier.endswith(".p"):
        return (
            f"OpenAI / chat parameter label ({topic}). Shown as a command option name or description.{hint}"
        )
    return f'UI copy for {topic}. English: "{src_preview}".{hint}'


def category_labels(pk: ParsedKey) -> list[str]:
    if not pk.parts:
        return ["command_name"] if pk.is_plain else []
    root = pk.parts[0]
    mapping = {
        "commands": "commands",
        "admin": "admin",
        "errors": "errors",
        "listeners": "listeners",
        "logs": "logs",
        "minigames": "minigames",
        "level": "leveling",
        "utility": "utility",
        "fun": "fun",
        "ai": "ai",
        "countries": "countries",
        "channel": "channel",
    }
    labels: list[str] = []
    if root in mapping:
        labels.append(mapping[root])
    if pk.is_params:
        if pk.field == "name":
            labels.append("command_option_name")
        elif pk.field == "description":
            labels.append("command_option_description")
        elif pk.field in {"true", "false"}:
            labels.append("command_option_choice")
        return _dedupe(labels)

    if pk.kind == "slash_command":
        if pk.field == "name":
            labels.append("command_name")
        elif pk.field == "description":
            labels.append("command_description")
        return _dedupe(labels)

    if pk.result_key and pk.field in {"title", "description"}:
        labels = [label for label in labels if label not in {"command_description", "command_name"}]
        labels.append("embed_title" if pk.field == "title" else "embed_description")
        rk = pk.result_key.lower()
        if rk in {"success", "completed", "added", "deletesuccess", "removed"}:
            labels.append("success")
        elif rk in {"forbidden", "http_error", "error", "failure", "failed", "notfound"}:
            labels.append("error")
        elif "permission" in rk:
            labels.append("warning")
        return _dedupe(labels)

    if pk.field == "title":
        labels.append("embed_title")
    elif pk.field == "description" and pk.subfield:
        labels.append("embed_field")
    elif pk.field == "description":
        labels.append("description")
    elif pk.field == "placeholder":
        labels.append("ui_placeholder")
    elif pk.field == "label":
        labels.append("ui_label")
    elif pk.field == "name" and pk.kind == "commands":
        labels.append("command_name")

    return _dedupe(labels)


def infer_max_length(pk: ParsedKey, labels: list[str]) -> int | None:
    if pk.is_plain:
        return 32
    if pk.result_key and pk.field in {"title", "description"}:
        return 256 if pk.field == "title" else 4096
    if "embed_title" in labels or pk.field == "title":
        return 256
    if "embed_description" in labels or (pk.field == "description" and "error" in labels):
        return 4096
    if "command_option_name" in labels or ("command_name" in labels):
        return 32
    if "command_description" in labels or "command_option_description" in labels:
        return 100
    if pk.kind == "slash_command" and pk.field == "description":
        return 100
    if pk.field in {"placeholder", "label"}:
        return 100
    if pk.field == "name":
        return 32
    return None


def _dedupe(labels: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for label in labels:
        if label not in seen:
            seen.add(label)
            out.append(label)
    return out


def enrich_entry(entry: dict[str, object], code_index: dict[str, set[str]]) -> dict[str, object]:
    identifier = str(entry.get("identifier", ""))
    source_string = str(entry.get("source_string", entry.get("translation", "")))
    pk = parse_identifier(identifier)

    entry["context"] = infer_context(identifier, source_string, pk, code_index)

    labels = category_labels(pk)
    entry["labels"] = ", ".join(labels)

    max_length = infer_max_length(pk, labels)
    if max_length is not None:
        entry["max_length"] = max_length

    return entry


def enrich_file(path: Path, code_index: dict[str, set[str]], dry_run: bool = False) -> tuple[int, int]:
    data: list[dict[str, object]] = json.loads(path.read_text(encoding="utf-8"))
    updated = 0
    for entry in data:
        if not isinstance(entry, dict):
            continue
        before = entry.get("context")
        enrich_entry(entry, code_index)
        if entry.get("context") != before:
            updated += 1
    if not dry_run:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(data), updated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--locale", action="append", help="Only process these locale codes")
    args = parser.parse_args()

    project_root = LOCALE_DIR.parent
    print("Indexing code references…")
    code_index = build_code_index(project_root)
    print(f"  {len(code_index)} keys mapped to source files")

    targets = args.locale if args.locale else LOCALES
    total_updated = 0
    for code in targets:
        path = LOCALE_DIR / f"{code}.json"
        if not path.exists():
            print(f"skip {code}: missing")
            continue
        count, updated = enrich_file(path, code_index, dry_run=args.dry_run)
        total_updated += updated
        print(f"{code}: {updated}/{count} contexts updated")
    print(f"done ({'dry run' if args.dry_run else 'written'})")


if __name__ == "__main__":
    main()
