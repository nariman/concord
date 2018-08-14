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
async def sample():
    """Returns sample context, positional and keyword arguments."""
    ctx = context.Context(None, None)
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
    async def test_middleware_run_method(self, sample):
        """Test that middleware `run` method works correctly and calls `next`
        function with provided arguments."""

        class SomeMiddleware(middleware.Middleware):
            async def run(self, ctx, next, *args, **kwargs):
                return await next(ctx, *args, **kwargs)

        mw = SomeMiddleware()
        sample_ctx, sample_args, sample_kwargs = sample

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
    async def test_middleware_function(self, sample):
        """Test that function can be wrapped into middleware."""

        async def some_middleware(ctx, next, *args, **kwargs):
            return await next(ctx, *args, **kwargs)

        mw = middleware.MiddlewareFunction(some_middleware)
        sample_ctx, sample_args, sample_kwargs = sample

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
        async def mw(ctx, _next, *args, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        assert isinstance(mw, middleware.MiddlewareFunction)
        # fmt: off
        assert await mw.run(
            sample_ctx, None, *sample_args, **sample_kwargs
        ) == 42
        # fmt: on

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

    def test_middleware_collection(self):
        """Test middleware collection class."""

        @middleware.as_middleware
        async def first_middleware(ctx, _next, *args, **kwargs):
            pass

        @middleware.as_middleware
        async def second_middleware(ctx, _next, *args, **kwargs):
            pass

        mc = middleware.MiddlewareCollection()
        mc.add_middleware(first_middleware)
        mc.add_middleware(second_middleware)

        assert set(mc.collection) == set([first_middleware, second_middleware])

    @pytest.mark.asyncio
    async def test_middleware_chain(self, sample):
        """Test middleware chaining.

        TODO: Should we check the order?
        """

        @middleware.as_middleware
        async def first_middleware(ctx, next, *args, **kwargs):
            return await next(ctx, *args, **kwargs) + 1

        @middleware.as_middleware
        async def second_middleware(ctx, next, *args, **kwargs):
            return await next(ctx, *args, **kwargs) + 2

        sample_ctx, sample_args, sample_kwargs = sample

        async def next(ctx, *args, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        chain = middleware.MiddlewareChain(first_middleware)
        chain.add_middleware(second_middleware)

        # fmt: off
        assert await chain.run(
            sample_ctx, next, *sample_args, **sample_kwargs
        ) == 42 + 1 + 2
        # fmt: on

    @pytest.mark.asyncio
    async def test_middleware_chain_decorator(self, sample):
        """Test middleware chaining via decorator.

        TODO: Tests for all cases of parameters.
        """

        async def second_middleware(ctx, next, *args, **kwargs):
            return await next(ctx, *args, **kwargs) + 2

        @middleware.middleware(second_middleware)
        async def first_middleware(ctx, next, *args, **kwargs):
            return await next(ctx, *args, **kwargs) + 1

        sample_ctx, sample_args, sample_kwargs = sample

        async def next(ctx, *args, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        assert isinstance(first_middleware, middleware.MiddlewareChain)
        # fmt: off
        assert await first_middleware.run(
            sample_ctx, next, *sample_args, **sample_kwargs
        ) == 42 + 1 + 2
        # fmt: on

    @pytest.mark.asyncio
    async def test_middleware_chain_call(self, sample):
        """Test that middleware chain can be called and the last middleware is
        called."""
        sample_ctx, sample_args, sample_kwargs = sample

        @middleware.as_middleware
        async def second_middleware(ctx, _next, *args, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 2

        @middleware.middleware(second_middleware)
        @middleware.as_middleware
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

    def test_middleware_group_class_is_abstract(self):
        """Test that middleware group subclass should implement methods.

        Class itself has no code to test, functionality can be tested on
        subclasses.
        """

        class SomeGroup(middleware.MiddlewareGroup):
            pass

        with pytest.raises(TypeError):
            SomeGroup()