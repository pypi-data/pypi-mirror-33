# Copyright 2018 John Reese
# Licensed under the MIT license

import asyncio
import operator
from typing import AsyncIterator, Callable

from .builtins import iter, list, next
from .types import AnyIterable, AnyIterableIterable, AnyStop, T

# infinite iterators


async def count(start: int = 0, step: int = 1) -> AsyncIterator[T]:
    value = start
    while True:
        yield value
        value += step


async def cycle(itr: AnyIterable) -> AsyncIterator[T]:
    source = list(itr)
    while True:
        for item in source:
            yield item


async def repeat(elem: T, n: int = -1) -> AsyncIterator[T]:
    while True:
        if n == 0:
            break
        yield elem
        n -= 1


# iterators terminating on shortest input sequence


async def accumulate(
    itr: AnyIterable, func: Callable[[T], T] = operator.add
) -> AsyncIterator[T]:
    itr = iter(itr)
    try:
        total: T = await next(itr)
    except AnyStop:
        return

    yield total
    if asyncio.iscoroutinefunction(func):
        async for item in itr:
            total = await func(total, item)
            yield total
    else:
        async for item in itr:
            total = func(total, item)
            yield total


async def chain(*itrs: AnyIterable) -> AsyncIterator[T]:
    async for itr in iter(itrs):
        async for item in iter(itr):
            yield item


def chain_from_iterable(itrs: AnyIterableIterable) -> AsyncIterator[T]:
    return chain(*itrs)


chain.from_iterable = chain_from_iterable
