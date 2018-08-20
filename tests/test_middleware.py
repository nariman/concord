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

from hugo import context
from hugo import middleware


@pytest.fixture(scope="function")
async def sample(bot_instance):
    """Returns sample context, positional and keyword arguments."""
    ctx = context.Context(bot_instance, None)
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
        function with provided arguments."""
        sample_ctx, sample_args, sample_kwargs = sample

        class SomeMiddleware(middleware.Middleware):
            async def run(self, ctx, next, *args, **kwargs):
                return await next(ctx, *args, **kwargs)

        mw = SomeMiddleware()

        async def next(ctx, *args, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        # fmt: off
        assert await mw.run(
            sample_ctx, next, *sample_args, **sample_kwargs
        ) == 42
        # fmt: on

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
        """Test that function can be wrapped into middleware."""
        sample_ctx, sample_args, sample_kwargs = sample

        async def some_middleware(ctx, next, *args, **kwargs):
            return await next(ctx, *args, **kwargs)

        mw = middleware.MiddlewareFunction(some_middleware)

        async def next(ctx, *args, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        # fmt: off
        assert await mw.run(
            sample_ctx, next, *sample_args, **sample_kwargs
        ) == 42
        # fmt: on

    @pytest.mark.asyncio
    async def test_middleware_function_decorator(self, sample):
        """Test that function can be wrapped into middleware via decorator."""
        sample_ctx, sample_args, sample_kwargs = sample

        @middleware.as_middleware
        async def mw(_ctx, _next, *args, **kwargs):
            pass

        assert isinstance(mw, middleware.MiddlewareFunction)

    @pytest.mark.asyncio
    async def test_middleware_function_call(self, sample):
        """Test that wrapped into middleware function can be called directly."""
        sample_ctx, sample_args, sample_kwargs = sample

        @middleware.as_middleware
        async def mw(ctx, _next, *args, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        assert await mw(sample_ctx, None, *sample_args, **sample_kwargs) == 42

    @pytest.mark.asyncio
    async def test_middleware_collection_class_is_abstract(self):
        """Test that middleware collection subclass should implement methods.

        Class itself has no code to test, functionality can be tested on
        subclasses.
        """

        class SomeCollection(middleware.MiddlewareCollection):
            pass

        class SomeImplementedCollection(middleware.MiddlewareCollection):
            async def run(self, _ctx, _next, *args, **kwargs):
                pass

        with pytest.raises(TypeError):
            SomeCollection()
        #
        with pytest.raises(TypeError):
            instance = SomeImplementedCollection()
            await instance()

    def test_middleware_collection(self):
        """Test middleware collection class."""

        class SomeCollection(middleware.MiddlewareCollection):
            async def run(self, _ctx, _next, *args, **kwargs):
                pass

        @middleware.as_middleware
        async def first_middleware(_ctx, _next, *args, **kwargs):
            pass

        @middleware.as_middleware
        async def second_middleware(_ctx, _next, *args, **kwargs):
            pass

        mc = SomeCollection()
        mc.add_middleware(first_middleware)
        mc.add_middleware(second_middleware)

        assert set(mc.collection) == set([first_middleware, second_middleware])

        # Accept only Middleware instances
        with pytest.raises(ValueError):
            mc.add_middleware(42)

    @pytest.mark.asyncio
    async def test_middleware_chain(self, sample):
        """Test middleware chaining.

        TODO: Check the order of running middleware.
        """
        sample_ctx, sample_args, sample_kwargs = sample

        @middleware.as_middleware
        async def first_middleware(ctx, next, *args, **kwargs):
            return await next(ctx, *args, **kwargs) + 1

        @middleware.as_middleware
        async def second_middleware(ctx, next, *args, **kwargs):
            return await next(ctx, *args, **kwargs) + 2

        async def next(ctx, *args, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        chain = middleware.MiddlewareChain()
        chain.add_middleware(first_middleware)
        chain.add_middleware(second_middleware)

        assert (
            await chain.run(sample_ctx, next, *sample_args, **sample_kwargs)
            == 42 + 1 + 2
        )

    @pytest.mark.asyncio
    async def test_middleware_chain_decorator(self, sample):
        """Test middleware chaining via decorator.

        TODO: Tests for all cases of parameters.
        """

        async def second_middleware(_ctx, _next, *args, **kwargs):
            pass

        @middleware.middleware(second_middleware)
        async def first_middleware(_ctx, _next, *args, **kwargs):
            pass

        assert isinstance(first_middleware, middleware.MiddlewareChain)

    @pytest.mark.asyncio
    async def test_middleware_chain_call(self, sample):
        """Test that middleware chain can be called and the last middleware is
        called."""
        sample_ctx, sample_args, sample_kwargs = sample

        async def second_middleware(ctx, _next, *args, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 2

        @middleware.middleware(second_middleware)
        async def first_middleware(ctx, _next, *args, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 1

        assert isinstance(first_middleware, middleware.MiddlewareChain)
        # fmt: off
        assert await first_middleware(
            sample_ctx, None, *sample_args, **sample_kwargs
        ) == 1
        # fmt: on

    @pytest.mark.asyncio
    async def test_one_of_all(self, sample):
        """Test OneOfAll class."""
        sample_ctx, sample_args, sample_kwargs = sample

        @middleware.as_middleware
        async def first_middleware(_ctx, _next, *args, **kwargs):
            return middleware.MiddlewareResult.IGNORE

        @middleware.as_middleware
        async def second_middleware(_ctx, _next, *args, **kwargs):
            return 2

        @middleware.as_middleware
        async def third_middleware(_ctx, _next, *args, **kwargs):
            return 3

        ooa = middleware.OneOfAll()
        ooa.add_middleware(first_middleware)
        ooa.add_middleware(second_middleware)
        ooa.add_middleware(third_middleware)

        # fmt: off
        assert await ooa.run(
            sample_ctx, None, *sample_args, **sample_kwargs
        ) == 2
        # fmt: on
        assert await ooa(sample_ctx, None, *sample_args, **sample_kwargs) == 2

        class NonCallableMiddleware(middleware.Middleware):
            async def run(self, _ctx, _next, *args, **kwargs):
                return middleware.MiddlewareResult.IGNORE

        ooa = middleware.OneOfAll()
        ooa.add_middleware(NonCallableMiddleware())
        ooa.add_middleware(NonCallableMiddleware())

        assert (
            await ooa.run(sample_ctx, None, *sample_args, **sample_kwargs)
            == middleware.MiddlewareResult.IGNORE
        )

        # All middleware is non-callable, should emulate non-callable
        with pytest.raises(TypeError):
            await ooa(sample_ctx, None, *sample_args, **sample_kwargs)
        #
        # A callable middleware is exists, should return unsuccessful result
        ooa.add_middleware(first_middleware)

        assert (
            await ooa(sample_ctx, None, *sample_args, **sample_kwargs)
            == middleware.MiddlewareResult.IGNORE
        )
