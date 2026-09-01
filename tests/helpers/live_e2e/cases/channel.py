from __future__ import annotations

from tests.helpers.live_e2e.cases._helpers import case

_CHANNEL = {"channel": "__main__"}

OVERRIDES = {
    "channel_name channel_ds_name channel_ds_add_name": case(
        "channel_name channel_ds_name channel_ds_add_name",
        option_overrides={**_CHANNEL, "seconds": 30},
        teardown="channel.ds_remove",
    ),
    "channel_name channel_ds_name channel_ds_get_name": case(
        "channel_name channel_ds_name channel_ds_get_name",
        setup="channel.ds_add",
    ),
    "channel_name channel_ds_name channel_ds_remove_name": case(
        "channel_name channel_ds_name channel_ds_remove_name",
        setup="channel.ds_add",
    ),
    "channel_name channel_farewell_name channel_farewell_set_ch_name": case(
        "channel_name channel_farewell_name channel_farewell_set_ch_name",
        option_overrides=_CHANNEL,
        teardown="channel.farewell_remove",
    ),
    "channel_name channel_farewell_name channel_farewell_remove_ch_name": case(
        "channel_name channel_farewell_name channel_farewell_remove_ch_name",
        setup="channel.farewell_set",
    ),
    "channel_name channel_media_name channel_media_name": case(
        "channel_name channel_media_name channel_media_name",
        option_overrides=_CHANNEL,
        teardown="channel.media_remove",
    ),
    "channel_name channel_media_name channel_mediaremove_name": case(
        "channel_name channel_media_name channel_mediaremove_name",
        setup="channel.media_set",
    ),
    "channel_name channel_welcome_name channel_w_name": case(
        "channel_name channel_welcome_name channel_w_name",
        option_overrides=_CHANNEL,
        teardown="channel.welcome_remove",
    ),
    "channel_name channel_welcome_name channel_w_remove_name": case(
        "channel_name channel_welcome_name channel_w_remove_name",
        setup="channel.welcome_set",
    ),
}
