import asyncio
import concurrent.futures
import functools

# Shared thread pool for I/O-bound blocking operations
_io_executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=4,
    thread_name_prefix="tanjun-io"
)

async def run_blocking(func, *args, **kwargs):
    """Run a blocking function in the thread pool to avoid blocking the event loop."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        _io_executor,
        functools.partial(func, *args, **kwargs)
    )
