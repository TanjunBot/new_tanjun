import json, sys
from collections import defaultdict

data = json.load(sys.stdin)
by_code = defaultdict(list)
for e in data:
    f = e["filename"].split("/new_tanjun/")[1]
    by_code[e["code"]].append((e["location"]["row"], f, e["message"]))

for code in sorted(by_code.keys()):
    items = by_code[code]
    print(f"\n=== {code} ({len(items)} occurrences) ===")
    for row, fname, msg in items[:10]:
        print(f"  L{row:>5} {fname:<55} {msg}")
    if len(items) > 10:
        print(f"  ... and {len(items)-10} more")
