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

import pytest

from hugo.core import middleware
from hugo.core.context import Context


@pytest.fixture(scope="function")
async def sample(client_instance):
    """Return sample context, positional and keyword arguments."""
    ctx = Context(client_instance, None)
    args = [1, "2"]
    kwargs = {"k": 1, "v": "2"}

    return ctx, args, kwargs


class TestMiddleware:
    """Test middleware module features."""

    def test_middleware_class_is_abstract(self):
        """Test that middleware should implement `run` method."""

        class SomeMiddleware(middleware.Middleware):
            pass

        with pytest.raises(TypeError):
            SomeMiddleware()

    @pytest.mark.asyncio
    async def test_middleware(self, sample):
        """Test that middleware `run` method works correctly and calls `next`
        function with provided arguments + test calling middleware as a
        function."""
        sample_ctx, sample_args, sample_kwargs = sample

        class SomeMiddleware(middleware.Middleware):
            async def run(self, *args, ctx, next, **kwargs):
                return await next(*args, ctx=ctx, **kwargs)

        mw = SomeMiddleware()

        async def next(*args, ctx, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        assert (
            await mw.run(
                *sample_args, ctx=sample_ctx, next=next, **sample_kwargs
            )
            == 42
        )
        assert (
            await mw(*sample_args, ctx=sample_ctx, next=next, **sample_kwargs)
            == 42
        )

    @pytest.mark.parametrize(
        "value",
        [
            middleware.MiddlewareResult.OK,
            middleware.MiddlewareResult.IGNORE,
            None,
            True,
            False,
            42,
            "42",
        ],
    )
    def test_middleware_successful_result_checker(self, value):
        """Tests `is_successful_result` method."""
        if value == middleware.MiddlewareResult.IGNORE:
            assert middleware.Middleware.is_successful_result(value) is False
        else:
            assert middleware.Middleware.is_successful_result(value) is True

    @pytest.mark.asyncio
    async def test_middleware_function(self, sample):
        """Test that function can be converted into a middleware."""
        sample_ctx, sample_args, sample_kwargs = sample

        async def async_middleware(*args, ctx, next, **kwargs):
            return await next(*args, ctx=ctx, **kwargs) + 1

        mw = middleware.MiddlewareFunction(async_middleware)

        async def next(*args, ctx, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        assert mw.fn == async_middleware
        assert (
            await mw.run(
                *sample_args, ctx=sample_ctx, next=next, **sample_kwargs
            )
            == 42 + 1
        )
        assert (
            await mw(*sample_args, ctx=sample_ctx, next=next, **sample_kwargs)
            == 42 + 1
        )

        def non_async_middleware(*args, ctx, next, **kwargs):
            pass

        with pytest.raises(ValueError):
            middleware.MiddlewareFunction(non_async_middleware)

    @pytest.mark.asyncio
    async def test_middleware_function_helper(self):
        """Test that function can be converted into a middleware via
        decorator."""

        async def mw(*args, ctx, next, **kwargs):
            pass

        converted_mw = middleware.as_middleware(mw)

        assert isinstance(converted_mw, middleware.MiddlewareFunction)
        assert converted_mw.fn == mw

    @pytest.mark.asyncio
    async def test_middleware_state(self, sample):
        """Test middleware state class.

        TODO: Too many repeated checks...
        """
        sample_ctx, sample_args, sample_kwargs = sample

        class State:
            pass

        sample_state = State()
        ms = middleware.MiddlewareState(sample_state)

        async def next(*args, ctx, **kwargs):
            assert ctx == sample_ctx
            assert hasattr(ctx, "states")
            assert ctx.states.get(State) == sample_state
            assert (
                middleware.MiddlewareState.get_state(ctx, State) == sample_state
            )
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        assert (
            await ms.run(
                *sample_args, ctx=sample_ctx, next=next, **sample_kwargs
            )
            == 42
        )

        ms = middleware.MiddlewareState(sample_state, key="sample_state_key")

        async def next(*args, ctx, sample_state_key, **kwargs):
            assert ctx == sample_ctx
            assert hasattr(ctx, "states")
            assert ctx.states.get(State) == sample_state
            assert (
                middleware.MiddlewareState.get_state(ctx, State) == sample_state
            )
            assert sample_state_key == sample_state
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        assert (
            await ms.run(
                *sample_args, ctx=sample_ctx, next=next, **sample_kwargs
            )
            == 42
        )

        class ContextState(middleware.MiddlewareState.ContextState):
            pass

        ms = middleware.MiddlewareState(ContextState, key="sample_state_key")

        async def next(*args, ctx, sample_state_key, **kwargs):
            assert ctx == sample_ctx
            assert isinstance(sample_state_key, ContextState)
            assert hasattr(ctx, "states")
            assert ctx.states.get(ContextState) == sample_state_key
            assert (
                middleware.MiddlewareState.get_state(ctx, ContextState)
                == sample_state_key
            )
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        assert (
            await ms.run(
                *sample_args, ctx=sample_ctx, next=next, **sample_kwargs
            )
            == 42
        )

    @pytest.mark.asyncio
    async def test_middleware_collection_class_is_abstract(self):
        """Test that middleware collection subclass should implement methods.

        Class itself has no code to test, functionality can be tested on
        subclasses.
        """

        class Collection(middleware.MiddlewareCollection):
            pass

        class ImplementedCollection(middleware.MiddlewareCollection):
            async def run(self, *args, ctx, next, **kwargs):
                pass

        with pytest.raises(TypeError):
            Collection()
        #
        with pytest.raises(TypeError):
            instance = ImplementedCollection()
            await instance()

    def test_middleware_collection(self):
        """Test middleware collection class."""

        class Collection(middleware.MiddlewareCollection):
            async def run(self, *args, ctx, next, **kwargs):
                pass

        @middleware.as_middleware
        async def first_middleware(*args, ctx, next, **kwargs):
            pass

        @middleware.as_middleware
        async def second_middleware(*args, ctx, next, **kwargs):
            pass

        mc = Collection()
        mc.add_middleware(first_middleware)
        mc.add_middleware(second_middleware)

        assert set(mc.collection) == set([first_middleware, second_middleware])

        # Accept only Middleware instances
        with pytest.raises(ValueError):
            mc.add_middleware(42)

    def test_middleware_collection_helper(self):
        """Test function to create collection with given middleware."""

        class Collection(middleware.MiddlewareCollection):
            async def run(self, *args, ctx, next, **kwargs):
                pass

        async def first_middleware(*args, ctx, next, **kwargs):
            pass

        @middleware.as_middleware
        async def second_middleware(*args, ctx, next, **kwargs):
            pass

        list_of_mw = [first_middleware, second_middleware]
        mc = middleware.collection_of(Collection, list_of_mw)

        assert isinstance(mc, Collection)
        assert set([mw.fn for mw in mc.collection]) == set(
            [first_middleware, second_middleware.fn]
        )

    @pytest.mark.asyncio
    async def test_middleware_chain(self, sample):
        """Test middleware chaining.

        TODO: Check the order of running middleware.
        """
        sample_ctx, sample_args, sample_kwargs = sample

        @middleware.as_middleware
        async def first_middleware(*args, ctx, next, **kwargs):
            return await next(*args, ctx=ctx, **kwargs) + 1

        @middleware.as_middleware
        async def second_middleware(*args, ctx, next, **kwargs):
            return await next(*args, ctx=ctx, **kwargs) + 2

        async def next(*args, ctx, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        chain = middleware.collection_of(
            middleware.MiddlewareChain, [first_middleware, second_middleware]
        )

        assert chain.fn == first_middleware.fn
        assert (
            await chain.run(
                *sample_args, ctx=sample_ctx, next=next, **sample_kwargs
            )
            == 42 + 1 + 2
        )
        assert (
            await chain(
                *sample_args, ctx=sample_ctx, next=next, **sample_kwargs
            )
            == 42 + 1 + 2
        )

    def test_middleware_chain_helper(self):
        """Test function to create chain with given middleware."""

        async def first_middleware(*args, ctx, next, **kwargs):
            pass

        @middleware.as_middleware
        async def second_middleware(*args, ctx, next, **kwargs):
            pass

        chain = middleware.chain_of([first_middleware, second_middleware])

        assert isinstance(chain, middleware.MiddlewareChain)
        assert set([mw.fn for mw in chain.collection]) == set(
            [first_middleware, second_middleware.fn]
        )

    @pytest.mark.asyncio
    async def test_middleware_chain_decorator(self, sample):
        """Test middleware chaining via decorator."""

        async def first_middleware(*args, ctx, next, **kwargs):
            pass

        async def second_middleware(*args, ctx, next, **kwargs):
            pass

        async def third_middleware(*args, ctx, next, **kwargs):
            pass

        chain = middleware.middleware(second_middleware)(first_middleware)
        assert isinstance(chain, middleware.MiddlewareChain)
        assert set([mw.fn for mw in chain.collection]) == set(
            [first_middleware, second_middleware]
        )

        chain = middleware.middleware(
            middleware.as_middleware(second_middleware)
        )(first_middleware)
        assert isinstance(chain, middleware.MiddlewareChain)
        assert set([mw.fn for mw in chain.collection]) == set(
            [first_middleware, second_middleware]
        )

        inner_chain = middleware.chain_of([first_middleware, second_middleware])
        chain = middleware.middleware(third_middleware)(inner_chain)
        assert isinstance(chain, middleware.MiddlewareChain)
        assert chain == inner_chain
        assert set([mw.fn for mw in chain.collection]) == set(
            [first_middleware, second_middleware, third_middleware]
        )

    @pytest.mark.asyncio
    async def test_one_of_all(self, sample):
        """Test OneOfAll class."""
        sample_ctx, sample_args, sample_kwargs = sample

        @middleware.as_middleware
        async def first_middleware(*args, ctx, next, **kwargs):
            return middleware.MiddlewareResult.IGNORE

        @middleware.as_middleware
        async def second_middleware(*args, ctx, next, **kwargs):
            return 2

        @middleware.as_middleware
        async def third_middleware(*args, ctx, next, **kwargs):
            return 3

        ooa = middleware.collection_of(
            middleware.OneOfAll,
            [first_middleware, second_middleware, third_middleware],
        )

        assert (
            await ooa.run(
                *sample_args, ctx=sample_ctx, next=None, **sample_kwargs
            )
            == 2
        )
        assert (
            await ooa(*sample_args, ctx=sample_ctx, next=None, **sample_kwargs)
            == 2
        )

        class NonCallableMiddleware(middleware.Middleware):
            async def run(self, *args, ctx, next, **kwargs):
                return middleware.MiddlewareResult.IGNORE

        ooa = middleware.OneOfAll()
        ooa.add_middleware(NonCallableMiddleware())

        assert (
            await ooa.run(
                *sample_args, ctx=sample_ctx, next=None, **sample_kwargs
            )
            == middleware.MiddlewareResult.IGNORE
        )
        assert (
            await ooa(*sample_args, ctx=sample_ctx, next=None, **sample_kwargs)
            == middleware.MiddlewareResult.IGNORE
        )
