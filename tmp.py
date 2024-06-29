from utility import get_xp_for_level, get_level_for_xp

scaling = "medium"
custom_formula = None

xps = [3, 100, 101, 150, 9000]

for xp in xps:
    level = get_level_for_xp(xp, scaling, custom_formula)
    print(level)
    xp_needed = get_xp_for_level(level, scaling, custom_formula)
    if level > 1:
        xp_for_last_level_needed = get_xp_for_level(level - 1, scaling, custom_formula)
    else:
        xp_for_last_level_needed = 0  # There's no XP needed for a level below 1

    print(
        f"XP: {xp}, Level: {level}, XP Needed: {xp_needed}, XP for last level needed: {xp_for_last_level_needed}"
    )
