from __future__ import annotations

from tests.helpers.live_e2e.cases._helpers import case

_CHANNEL = {"channel": "__main__"}

OVERRIDES = {
    "minigame_name minigames_countingcmds_name minigames_setcountingch_name": case(
        "minigame_name minigames_countingcmds_name minigames_setcountingch_name",
        option_overrides=_CHANNEL,
        teardown="minigames.remove_counting",
    ),
    "minigame_name minigames_countingcmds_name minigames_removecountingch_name": case(
        "minigame_name minigames_countingcmds_name minigames_removecountingch_name",
        setup="minigames.set_counting",
    ),
    "minigame_name minigames_countingcmds_name minigames_setcprogress_name": case(
        "minigame_name minigames_countingcmds_name minigames_setcprogress_name",
        option_overrides={"progress": 0},
        setup="minigames.set_counting",
    ),
    "minigame_name minigames_wordchaincmds_name minigames_setwordcainch_name": case(
        "minigame_name minigames_wordchaincmds_name minigames_setwordcainch_name",
        option_overrides=_CHANNEL,
        teardown="minigames.remove_wordchain",
    ),
    "minigame_name minigames_wordchaincmds_name minigames_removewordchch_name": case(
        "minigame_name minigames_wordchaincmds_name minigames_removewordchch_name",
        setup="minigames.set_wordchain",
    ),
}
