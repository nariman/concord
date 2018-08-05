"""
The MIT License (MIT)

Copyright (c) 2017-2018 Nariman Safiulin

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import abc

from . import context


class Middleware(abc.ABC):
    """Discord message processing middleware.

    Middleware are useful for filtering events or extending functionality.
    """

    @abc.abstractmethod
    async def run(self, ctx: context.Context, next, *args, **kwargs):
        """Middleware's main logic.

        Parameters
        ----------
        ctx : context.Context
            Discord message processing context.

            .. note:
                Provided context can be replaced and passed to the next
                middleware, but do it only if needed.

        next : callable
            The next function to call. Not necessarily a middleware. Pass
            context and all positional and keyword arguments, even if unused.
            Should be awaited.
        """
        pass


class MiddlewareFunction(Middleware):
    """Middleware class for wrapping functions into valid middleware.

    Attributes
    ----------
    fn : callable
        A function to wrap as a middleware. Should be a coroutine.
    """

    def __init__(self, fn):
        self.fn = fn

    async def run(self, ctx: context.Context, next, *args, **kwargs):
        return await self.fn(ctx, next, *args, **kwargs)

    async def __call__(self, *args, **kwargs):
        """Invokes function with given parameters."""
        return await self.fn(*args, **kwargs)


class MiddlewareChain(Middleware):
    """Class for chaining middleware. It's a middleware itself.

    Attributes
    ----------
    chain : list[Middleware]
        List of middleware to run in a certain order. The first items is a
        last-to-call middleware (in other words, list is reversed).
    """

    def __init__(self, middleware: Middleware):
        self.chain = [middleware]

    async def run(self, ctx: context.Context, next, *args, **kwargs):
        # Oh dear! Please, rewrite it...
        for current in self.chain:
            next = (
                lambda current, next: lambda ctx, *args, **kwargs: current.run(
                    ctx, next, *args, **kwargs
                )
            )(current, next)

        return await next(ctx, *args, **kwargs)

    async def __call__(self, *args, **kwargs):
        """Invokes last middleware with given parameters.

        It makes sense only if last middleware is a wrapped function."""
        return await self.chain[0](*args, **kwargs)


def as_middleware(fn):
    """Wrap function into a middleware."""
    return MiddlewareFunction(fn)


def middleware(outer_middleware: Middleware):
    """Append a middleware to the chain.

    Parameters
    ----------
    outer_middleware : Middleware
        A middleware to append to the chain.
    """
    if not isinstance(outer_middleware, Middleware):
        raise ValueError("Outer middleware should be a `Middleware` instance.")
    # fmt: off

    def decorator(inner_middleware: Middleware):
        if not isinstance(inner_middleware, Middleware):
            raise ValueError(
                "Inner middleware should be a `Middleware` instance."
            )

        if isinstance(inner_middleware, MiddlewareChain):
            middleware_chain = inner_middleware
        else:
            middleware_chain = MiddlewareChain(inner_middleware)

        middleware_chain.chain.append(outer_middleware)
        return middleware_chain
    # fmt: on

    return decorator
