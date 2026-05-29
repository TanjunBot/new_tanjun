"""Time-related utilities: relative time string parsing and date formatting.

Extracted from ``utility.py`` as part of refactoring (issue #1608).
"""

import datetime
import re


def relative_time_str_to_date(time_string: str) -> datetime.datetime:
    if not time_string:
        return datetime.datetime.now()

    pattern = r"(\d+)([smhd])"
    matches = re.findall(pattern, time_string.lower())

    if not matches:
        return datetime.datetime.now()

    days = hours = minutes = seconds = 0

    for value, unit in matches:
        value = int(value)
        if unit == "s":
            seconds += value
        elif unit == "m":
            minutes += value
        elif unit == "h":
            hours += value
        elif unit == "d":
            days += value

    delta = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return datetime.datetime.now() + delta


def relative_time_to_seconds(time_string: str) -> int:
    if not time_string:
        return 0

    pattern = r"(\d+)([smhd])"
    matches = re.findall(pattern, time_string.lower())

    if not matches:
        return 0

    days = hours = minutes = seconds = 0

    for value, unit in matches:
        value = int(value)
        if unit == "s":
            seconds += value
        elif unit == "m":
            minutes += value
        elif unit == "h":
            hours += value
        elif unit == "d":
            days += value

    delta = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return int(delta.total_seconds())


def dateToRelativeTimeStr(date: datetime.datetime) -> str:  # noqa: N802
    start_date = datetime.datetime.now()
    total_seconds = (date - start_date).total_seconds()

    is_negative = total_seconds < 0
    abs_seconds = abs(total_seconds)

    days = int(abs_seconds // 86400)
    remaining_seconds = int(abs_seconds % 86400)
    hours = remaining_seconds // 3600
    minutes = (remaining_seconds % 3600) // 60
    seconds = remaining_seconds % 60

    components = []
    if days:
        components.append(f"{days}d")
    if hours:
        components.append(f"{hours}h")
    if minutes:
        components.append(f"{minutes}m")
    if seconds:
        components.append(f"{seconds}s")

    result = " ".join(components)
    return f"-{result}" if is_negative and result else result


def date_time_to_timestamp(date: datetime.datetime) -> int:
    return int(date.timestamp())


def isoTimeToDate(isoTime: str) -> datetime.datetime:  # noqa: N802,N803
    return datetime.datetime.fromisoformat(isoTime)


# Backward-compatible aliases
relativeTimeStrToDate = relative_time_str_to_date  # noqa: N816
relativeTimeToSeconds = relative_time_to_seconds  # noqa: N816
