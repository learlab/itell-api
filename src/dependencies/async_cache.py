"""
Helpers to use [cachetools](https://github.com/tkem/cachetools) with
asyncio.
Modified from unmaintained [asyncache](https://github.com/hephex/asyncache)
"""

import asyncio
import functools

from cachetools import Cache, keys


def acached(
    cache: Cache,
    lock: asyncio.Lock = asyncio.Lock(),
    key=keys.hashkey,
):
    """
    Decorator to wrap a coroutine with a memoizing callable
    that saves results in a cache.
    """

    def decorator(func):
        assert asyncio.iscoroutinefunction(func), "Function must be a coroutine."

        async def wrapper(*args, **kwargs):
            k = key(*args, **kwargs)
            try:
                async with lock:
                    return cache[k]

            except KeyError:
                pass  # key not found

            val = await func(*args, **kwargs)

            try:
                async with lock:
                    cache[k] = val

            except ValueError:
                pass  # val too large

            return val

        return functools.update_wrapper(wrapper, func)

    return decorator
