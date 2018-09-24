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

from hugo.core.middleware import MiddlewareFunction, as_middleware


def test_function_converting():
    async def mw(*args, ctx, next, **kwargs):
        pass

    assert MiddlewareFunction(mw).fn == mw


def test_function_constraints():
    def mw(*args, ctx, next, **kwargs):
        pass

    with pytest.raises(ValueError):
        MiddlewareFunction(mw)


@pytest.mark.asyncio
async def test_running_behaviour(context, sample_parameters):
    sa, skwa = sample_parameters

    async def async_mw(*args, ctx, next, **kwargs):
        return await next(*args, ctx=ctx, **kwargs) + 1

    mw = MiddlewareFunction(async_mw)

    async def next(*args, ctx, **kwargs):
        assert ctx == context and list(args) == sa and kwargs == skwa
        return 42

    assert await mw.run(*sa, ctx=context, next=next, **skwa) == 42 + 1


@pytest.mark.asyncio
async def test_helper():
    async def mw(*args, ctx, next, **kwargs):
        pass

    converted_mw = as_middleware(mw)

    assert isinstance(converted_mw, MiddlewareFunction)
    assert converted_mw.fn == mw
