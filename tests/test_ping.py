# Unused imports:
# import time


async def test_ping(self, ctx):
    ping = ctx.bot.latency * 1000
    if ping > 1000:
        raise Exception(f"Ping too high: {ping:.2f}ms")
    return ping
