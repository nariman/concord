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
    """Return sample context, positional and keyword arguments."""
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

        async def some_middleware(*args, ctx, next, **kwargs):
            return await next(*args, ctx=ctx, **kwargs) + 1

        mw = middleware.MiddlewareFunction(some_middleware)

        async def next(*args, ctx, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        assert mw.fn == some_middleware
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

    @pytest.mark.asyncio
    async def test_middleware_function_decorator(self, sample):
        """Test that function can be converted into a middleware via
        decorator."""

        async def mw(*args, ctx, next, **kwargs):
            pass

        converted_mw = middleware.as_middleware(mw)

        assert isinstance(converted_mw, middleware.MiddlewareFunction)
        assert converted_mw.fn == mw

    @pytest.mark.asyncio
    async def test_middleware_function_as_a_class_method(self, sample):
        """Test that class methods can be converted into a middleware without
        problems."""
        sample_ctx, sample_args, sample_kwargs = sample

        class TestClass:
            @middleware.as_middleware
            async def first_middleware(self, *args, ctx, next, **kwargs):
                assert isinstance(self, TestClass)

                assert ctx == sample_ctx
                assert sample_args == list(args)
                assert sample_kwargs == kwargs

                return await next(*args, ctx=ctx, **kwargs)

            async def second_middleware(self, *args, ctx, next, **kwargs):
                pass

        async def next(*args, ctx, **kwargs):
            assert ctx == sample_ctx
            assert sample_args == list(args)
            assert sample_kwargs == kwargs

            return 42

        tc = TestClass()

        assert (
            await tc.first_middleware.run(
                tc, *sample_args, ctx=sample_ctx, next=next, **sample_kwargs
            )
            == 42
        )
        assert (
            await tc.first_middleware(
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

        class SomeCollection(middleware.MiddlewareCollection):
            pass

        class SomeImplementedCollection(middleware.MiddlewareCollection):
            async def run(self, *args, ctx, next, **kwargs):
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
            async def run(self, *args, ctx, next, **kwargs):
                pass

        @middleware.as_middleware
        async def first_middleware(*args, ctx, next, **kwargs):
            pass

        @middleware.as_middleware
        async def second_middleware(*args, ctx, next, **kwargs):
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

        chain = middleware.MiddlewareChain()
        chain.add_middleware(first_middleware)
        chain.add_middleware(second_middleware)

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

    @pytest.mark.asyncio
    async def test_middleware_chain_decorator(self, sample):
        """Test middleware chaining via decorator.

        TODO: Tests for all cases of parameters.
        """

        async def second_middleware(*args, ctx, next, **kwargs):
            pass

        async def first_middleware(*args, ctx, next, **kwargs):
            pass

        chain = middleware.middleware(second_middleware)(first_middleware)

        assert isinstance(chain, middleware.MiddlewareChain)
        assert chain.fn == first_middleware

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

        ooa = middleware.OneOfAll()
        ooa.add_middleware(first_middleware)
        ooa.add_middleware(second_middleware)
        ooa.add_middleware(third_middleware)

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
