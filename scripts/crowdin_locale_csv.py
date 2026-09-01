#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

LOCALE_DIR = Path(__file__).resolve().parent.parent / "locales"
CSV_FIELDS = ("identifier", "source_phrase", "translation", "context", "labels", "max_length")
JSON_TO_CSV = {
    "identifier": "identifier",
    "source_string": "source_phrase",
    "translation": "translation",
    "context": "context",
    "labels": "labels",
    "max_length": "max_length",
}


def json_row_to_csv(row: dict[str, object]) -> dict[str, str]:
    out: dict[str, str] = {}
    for json_key, csv_key in JSON_TO_CSV.items():
        value = row.get(json_key, "")
        if value is None:
            out[csv_key] = ""
        else:
            out[csv_key] = str(value)
    return out


def csv_row_to_json(row: dict[str, str]) -> dict[str, object]:
    max_length_raw = row.get("max_length", "").strip()
    max_length: int | None
    if not max_length_raw:
        max_length = None
    elif max_length_raw.isdigit():
        max_length = int(max_length_raw)
    else:
        max_length = None
    return {
        "identifier": row.get("identifier", ""),
        "source_string": row.get("source_phrase", ""),
        "translation": row.get("translation", ""),
        "context": row.get("context", ""),
        "labels": row.get("labels", ""),
        "max_length": max_length,
    }


def to_csv(locales: list[str] | None) -> int:
    paths = [LOCALE_DIR / f"{code}.json" for code in locales] if locales else sorted(LOCALE_DIR.glob("*.json"))
    count = 0
    for json_path in paths:
        if not json_path.exists():
            continue
        with json_path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            raise ValueError(f"{json_path} must be a JSON array")
        csv_path = json_path.with_suffix(".csv")
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
            writer.writeheader()
            for row in data:
                if isinstance(row, dict):
                    writer.writerow(json_row_to_csv(row))
        count += 1
    return count


def to_json(locales: list[str] | None) -> int:
    paths = [LOCALE_DIR / f"{code}.csv" for code in locales] if locales else sorted(LOCALE_DIR.glob("*.csv"))
    count = 0
    for csv_path in paths:
        if not csv_path.exists():
            continue
        with csv_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        json_path = csv_path.with_suffix(".json")
        payload = [csv_row_to_json(row) for row in rows]
        json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func in (("to-csv", to_csv), ("to-json", to_json)):
        cmd = sub.add_parser(name)
        cmd.add_argument("--locale", action="append", help="Locale code (e.g. en, de). Default: all locale files.")
    args = parser.parse_args()
    locales = args.locale if hasattr(args, "locale") else None
    if args.command == "to-csv":
        n = to_csv(locales)
    else:
        n = to_json(locales)
    print(n)


if __name__ == "__main__":
    main()
