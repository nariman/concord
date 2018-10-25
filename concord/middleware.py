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
import asyncio
import enum
from typing import Any, Callable, List, Optional, Sequence, Type, TypeVar, Union

from concord.context import Context


class MiddlewareResult(enum.Enum):
    """Enum values for middleware results.

    One of these values can be returned by a middleware instead of actual data.
    Anything returned by the middleware and is not an enum value is considered
    as successful result (``OK`` value).
    """

    OK = enum.auto()
    IGNORE = enum.auto()


def is_successful_result(value: Union[MiddlewareResult, Any]) -> bool:
    """Returns ``True``, if given value is a successful middleware result."""
    if value == MiddlewareResult.IGNORE:
        return False
    return True


class Middleware(abc.ABC):
    """Event processing middleware.

    Middleware are useful for filtering events or extending functionality.

    They could return something or nothing (``None``) to indicate success,
    otherwise :class:`MiddlewareResult` values can be used.

    Functions can also be converted into a middleware by using
    :class:`MiddlewareFunction` or :func:`as_middleware` decorator.

    Attributes:
        fn: A source function, when a last middleware in a middleware chain is
            a :class:`MiddlewareFunction` or it is the
            :class:`MiddlewareFunction` itself.
            Can be not present, if the middleware chain is created not with
            :func:`middleware` decorator, or there is complex middleware tree.

            .. seealso::
                :class:`MiddlewareChain`.
    """

    fn: Optional[Callable]

    def __init__(self):
        self.fn = None

    @abc.abstractmethod
    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:
        """Middleware's main logic.

        .. note::
            Context ``ctx`` and ``next`` callable are keyword parameters.

        Args:
            ctx: Event processing context.

                .. note::
                    Provided context can be replaced and passed to the ``next``
                    callable, but do it only if needed.

            next: The next function to call. Not necessarily a middleware. Pass
                context, all positional and keyword parameters, even if unused.
                Must be awaited.

        Returns:
            Middleware data or :class:`MiddlewareResult` enum value.
        """
        pass  # pragma: no cover

    @staticmethod
    def is_successful_result(value: Union[MiddlewareResult, Any]) -> bool:
        """Returns ``True``, if given value is a successful middleware
        result."""
        return is_successful_result(value)

    async def __call__(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:
        """Invokes the middleware with given parameters."""
        return await self.run(*args, ctx=ctx, next=next, **kwargs)


class MiddlewareFunction(Middleware):
    """Middleware to use function (any callable) as a valid middleware.

    Args:
        fn: A function to use as a middleware. Should be a coroutine.

    Raises:
        ValueError: If the given function is not a coroutine.

    Attributes:
        fn: The source function to use as a middleware. A coroutine.
    """

    def __init__(self, fn: Callable):
        super().__init__()

        if not asyncio.iscoroutinefunction(fn):
            raise ValueError("Not a coroutine")
        self.fn = fn

    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:
        return await self.fn(*args, ctx=ctx, next=next, **kwargs)


class MiddlewareState(Middleware):
    """Middleware that can provide a given state within a middleware tree.

    It is an alternative to middleware as class methods.

    Every state will be saved in a context and could be found by state's type
    (see :meth:`get_state`). If you also want to pass the state as a parameter,
    provide a ``key`` parameter name.

    You can use :meth:`get_state` helper to get the state from the context. It
    is especially useful, when ``key`` is not provided.

    If a class provided as the state, it will be instantiated for you on first
    middleware run.
    If a :class:`ContextState` subclass provided as the state, it will be
    instantiated for you on every middleware run.

    Args:
        state: A state to provide.
        key: A parameter name, by which the state will be provided.

    Attributes:
        state: The state for providing.
        key: The parameter name, by which the state will be provided as a
            parameter, if present.
    """

    StateType = TypeVar("StateType")

    class ContextState:
        """State that should be instantiated on every middleware run.

        Your state should subclass it.
        """

        pass

    state: Any
    key: Optional[str]

    def __init__(self, state: Any, *, key: Optional[str] = None):
        super().__init__()
        self.state = state
        self.key = key

    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:  # noqa: D102
        state = self.state
        if isinstance(state, type):
            if issubclass(state, MiddlewareState.ContextState):
                state = state()
            else:
                self.state = state = state()

        if self.key:
            kwargs[self.key] = state
        self.set_state(ctx, state)

        return await next(*args, ctx=ctx, **kwargs)

    @staticmethod
    def get_state(
        ctx: Context, state_type: Type[StateType]
    ) -> Optional[StateType]:
        """Returns a state from the context."""
        MiddlewareState._ensure_context(ctx)
        return ctx.states.get(state_type)

    @staticmethod
    def set_state(ctx: Context, state: Any) -> None:
        """Sets the state to the context."""
        MiddlewareState._ensure_context(ctx)
        ctx.states[type(state)] = state

    @staticmethod
    def _ensure_context(ctx: Context) -> None:
        """Checks is the context has states storage, and creates it if
        necessary."""
        if getattr(ctx, "states", None) is None:
            ctx.states = dict()


class MiddlewareCollection(Middleware, abc.ABC):
    """Abstract class for grouping middleware. It is a middleware itself.

    Method :meth:`run` is abstract. Each subclass should implement own behavior
    of how to run group of middleware. For example, run middleware in specific
    order, run middleware until desired results is obtained, etc. Useful, when
    it is known, what middleware can return.

    Attributes:
        collection: List of middleware to run. Take a note that order of
            middleware in the list can be used in an implementation.
    """

    collection: List[Middleware]

    def __init__(self):
        super().__init__()
        self.collection = []

    def add_middleware(self, middleware: Middleware) -> Middleware:
        """Adds middleware to the list.

        Can be used as a decorator.

        Args:
            middleware: A middleware to add to the list.

        Returns:
            The given middleware.

        Raises:
            ValueError: If given parameter is not a middleware.
        """
        if not isinstance(middleware, Middleware):
            raise ValueError("Not a middleware")
        #
        self.collection.append(middleware)
        return middleware

    @abc.abstractmethod
    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:  # noqa: D102
        pass  # pragma: no cover


class MiddlewareChain(MiddlewareCollection):
    """Middleware collection for chaining middleware.

    Attributes:
        collection: List of middleware to run in a certain order. The first
            items is a last-to-call middleware (in other words, list is
            reversed).
    """

    def add_middleware(
        self, middleware: Middleware
    ) -> Middleware:  # noqa: D102
        super().add_middleware(middleware)
        if len(self.collection) == 1:
            self.fn = middleware.fn
        return middleware

    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:  # noqa: D102
        for current in self.collection:
            # We need to save `current` and `next` middleware in a separate
            # context for each step. Lambda is a life-hack.
            # It constructs first lambda with last-to-call middleware and `next`
            # callable, given by outer scope and runs it. Result is an another
            # lambda, that is can be used as an `next` callable.
            # Result lambda overwrites `next` in our scope, next cycle uses the
            # next middleware in chain order and overwritten `next` callable.
            # In the end, a lambda chain will be constructed.
            next = (
                lambda current, next: lambda *args, ctx, **kwargs: current.run(
                    *args, ctx=ctx, next=next, **kwargs
                )
            )(current, next)
        return await next(*args, ctx=ctx, **kwargs)


class MiddlewareSequence(MiddlewareCollection):
    """Middleware collection for sequencing middleware.

    It processes all of the middleware list and returns a tuple of results. But
    it returns unsuccessful result if all of the results is unsuccessful.

    See :class:`Middleware` for information about successful results.
    """

    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:  # noqa: D102
        results = []
        successful = False

        for mw in self.collection:
            result = await mw.run(*args, ctx=ctx, next=next, **kwargs)
            results.append(result)
            if not successful and self.is_successful_result(result):
                successful = True
        #
        if successful:
            return tuple(results)
        return MiddlewareResult.IGNORE


def as_middleware(fn: Callable) -> MiddlewareFunction:
    """Creates a middleware for given function (or any callable).

    If you are planning to chain this function with another middleware, just use
    :func:`middleware` helper. It will create a middleware from the function for
    you, if needed.

    Args:
        fn: A function to use as a middleware.

    Returns:
        Middleware for given function.
    """
    # We don't care, when somebody is converting a middleware into another one...
    return MiddlewareFunction(fn)


def collection_of(
    collection_class: Type[MiddlewareCollection],
    middleware: Sequence[Union[Middleware, Callable]],
) -> MiddlewareCollection:
    """Creates a new collection of given middleware.

    If any of given parameters is not a middleware, a middleware will be created
    for it for you.

    Args:
        collection_class: A collection class to create collection of.
        middleware: List of middleware to create collection of.

    Returns:
        Instance of given collection class with the list of middleware in the
        collection.
    """
    collection = collection_class()

    for mw in middleware:
        if not isinstance(mw, Middleware):
            mw = as_middleware(mw)
        collection.add_middleware(mw)
    #
    return collection


def chain_of(
    middleware: Sequence[Union[Middleware, Callable]]
) -> MiddlewareChain:
    """Creates a new chain (:class:`MiddlewareChain`) of given middleware.

    If any of given parameters is not a middleware, a middleware will be created
    for it for you.

    Args:
        middleware: List of middleware to create chain of.

    Returns:
        Chain of given middleware.
    """
    return collection_of(MiddlewareChain, middleware)


def sequence_of(
    middleware: Sequence[Union[Middleware, Callable]]
) -> MiddlewareChain:
    """Creates a new sequence (:class:`MiddlewareSequence`) of given middleware.

    If any of given parameters is not a middleware, a middleware will be created
    for it for you.

    Args:
        middleware: A list of middleware to create chain of.

    Returns:
        Sequence of given middleware.
    """
    return collection_of(MiddlewareSequence, middleware)


def middleware(outer_middleware: Middleware):
    """Appends a middleware to the chain. A decorator.

    If decorated function is not a middleware, a middleware will be created
    for it by the decorator.

    Args:
        outer_middleware: A middleware to append to the chain.
    """
    if not isinstance(outer_middleware, Middleware):
        outer_middleware = as_middleware(outer_middleware)

    def decorator(inner_middleware: Middleware) -> MiddlewareChain:
        # If we already have a chain under the decorator, just add to it.
        if isinstance(inner_middleware, MiddlewareChain):
            inner_middleware.add_middleware(outer_middleware)
            return inner_middleware
        #
        return chain_of([inner_middleware, outer_middleware])

    return decorator


class OneOfAll(MiddlewareCollection):
    """Middleware collection with "first success" condition.

    It processes the middleware list until one of them returns a successful
    result.

    See :class:`Middleware` for information about successful results.
    """

    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:  # noqa: D102
        for mw in self.collection:
            result = await mw.run(*args, ctx=ctx, next=next, **kwargs)
            if self.is_successful_result(result):
                return result
        #
        return MiddlewareResult.IGNORE
