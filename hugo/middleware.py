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
import enum
import typing

from . import context


class MiddlewareResult(enum.Enum):
    """Enum values for middleware results.

    One of these values can be returned in a middleware instead of actual data.
    Anything returned by a middleware and isn't a enum value is considered as a
    success of the process.
    """

    OK = enum.auto()
    IGNORE = enum.auto()


class Middleware(abc.ABC):
    """Event processing middleware.

    Middleware are useful for filtering events or extending functionality.

    Middleware should return something (even `None`) to indicate success,
    otherwise :class:`MiddlewareResult` values can be used.
    """

    @abc.abstractmethod
    async def run(self, ctx: context.Context, next, *args, **kwargs):
        """Middleware's main logic.

        Parameters
        ----------
        ctx : :class:`.context.Context`
            Discord message processing context.

            .. note::
                Provided context can be replaced and passed to the next
                middleware, but do it only if needed.

        next : callable
            The next function to call. Not necessarily a middleware. Pass
            context and all positional and keyword arguments, even if unused.
            Should be awaited.

        Returns
        -------
        :class:`MiddlewareResult`
            A enum value when no actual data can be provided.
        :any:`typing.Any`
            Middleware data.
        """
        pass


class MiddlewareFunction(Middleware):
    """Middleware class for wrapping functions into valid middleware.

    Parameters
    ----------
    fn : callable
        A function to wrap as a middleware. Should be a coroutine.

    Attributes
    ----------
    fn : callable
        A function wrapped as a middleware. A coroutine.
    """

    def __init__(self, fn):
        self.fn = fn

    async def run(self, ctx: context.Context, next, *args, **kwargs):
        return await self.fn(ctx, next, *args, **kwargs)

    async def __call__(self, *args, **kwargs):
        """Invokes function with given parameters."""
        return await self.fn(*args, **kwargs)


class MiddlewareCollection:
    """Class for process list of middleware in some order and rules.

    Attributes
    ----------
    collection : List[:class:`Middleware`]
        List of middleware.
    """

    def __init__(self):
        self.collection = []

    def add_middleware(self, middleware: Middleware):
        """Add middleware to the list.

        Parameters
        ----------
        middleware : :class:`Middleware`
            A middleware to add to the list.
        """
        self.collection.append(middleware)


class MiddlewareChain(Middleware, MiddlewareCollection):
    """Class for chaining middleware. It's a middleware itself.

    Parameters
    ----------
    middleware: :class:`Middleware`
        The initial middleware in the chain.

    Attributes
    ----------
    collection : List[:class:`Middleware`]
        List of middleware to run in a certain order. The first items is a
        last-to-call middleware (in other words, list is reversed).
    """

    def __init__(self, middleware: Middleware):
        super().__init__()
        self.add_middleware(middleware)

    async def run(self, ctx: context.Context, next, *args, **kwargs):
        # Oh dear! Please, rewrite it...
        for current in self.collection:
            next = (
                lambda current, next: lambda ctx, *args, **kwargs: current.run(
                    ctx, next, *args, **kwargs
                )
            )(current, next)
        return await next(ctx, *args, **kwargs)

    async def __call__(self, *args, **kwargs):
        """Invokes last middleware with given parameters.

        It makes sense only if last middleware is a wrapped function."""
        return await self.collection[0](*args, **kwargs)


class MiddlewareGroup(Middleware, MiddlewareCollection, abc.ABC):
    """Class for grouping middleware. It's a middleware itself.

    Method :meth:`run` is abstract. Each subclass should implement own behavior
    of how to run group of middleware. For example, run only one middleware, if
    success, or run all middleware, or run middleware until desired results is
    obtained, etc. Useful, when it's known, what middleware can return.

    Method :meth:`__call__` is abstract as well.

    Attributes
    ----------
    collection : List[:class:`Middleware`]
        List of middleware to run. Take a note that middleware will be run in
        the order of they're in the list.
    """

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    async def run(self, ctx: context.Context, next, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def __call__(self, *args, **kwargs):
        pass


def as_middleware(fn):
    """Wrap function into a middleware."""
    if isinstance(fn, Middleware):
        raise ValueError("Already a middleware.")
    return MiddlewareFunction(fn)


def middleware(outer_middleware: Middleware):
    """Append a middleware to the chain.

    If decorated function is not a middleware, it will be wrapped into
    middleware by decorator.

    Parameters
    ----------
    outer_middleware : :class:`Middleware`
        A middleware to append to the chain.
    """
    if not isinstance(outer_middleware, Middleware):
        outer_middleware = as_middleware(outer_middleware)
    # fmt: off

    def decorator(inner_middleware: Middleware):
        if isinstance(inner_middleware, MiddlewareChain):
            middleware_chain = inner_middleware
        elif isinstance(inner_middleware, Middleware):
            middleware_chain = MiddlewareChain(inner_middleware)
        else:
            middleware_chain = MiddlewareChain(as_middleware(inner_middleware))

        middleware_chain.add_middleware(outer_middleware)
        return middleware_chain
    # fmt: on

    return decorator
