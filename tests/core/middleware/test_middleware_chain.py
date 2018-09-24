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

from hugo.core.middleware import (
    MiddlewareChain,
    chain_of,
    collection_of,
    middleware,
)


# We use `collection_of` instead of direct instance of `MiddlewareChain` because
# we assume that `collection_of` has tested and ok to use and due to the same
# logic under the hood of `collection_of`.


@pytest.mark.asyncio
async def test_function_propagation():
    async def first_mw(*args, ctx, next, **kwargs):
        pass

    async def second_mw(*args, ctx, next, **kwargs):
        pass

    chain = collection_of(MiddlewareChain, [first_mw, second_mw])
    assert chain.fn == first_mw


@pytest.mark.asyncio
async def test_running_behaviour(context, sample_parameters):
    sa, skwa = sample_parameters

    async def first_mw(*args, ctx, next, **kwargs):
        return await next(*args, ctx=ctx, **kwargs) + 1

    async def second_mw(*args, ctx, next, **kwargs):
        return await next(*args, ctx=ctx, **kwargs) + 2

    async def next(*args, ctx, **kwargs):
        assert ctx == context and list(args) == sa and kwargs == skwa
        return 42

    chain = collection_of(MiddlewareChain, [first_mw, second_mw])
    assert await chain.run(*sa, ctx=context, next=next, **skwa) == 42 + 1 + 2


def test_helper():
    async def first_mw(*args, ctx, next, **kwargs):
        pass

    async def second_mw(*args, ctx, next, **kwargs):
        pass

    chain = chain_of([first_mw, second_mw])
    # Just check that, `collection_of` covers all of the other stuff to check.
    assert isinstance(chain, MiddlewareChain)


@pytest.mark.asyncio
async def test_decorator():
    async def first_mw(*args, ctx, next, **kwargs):
        pass

    async def second_mw(*args, ctx, next, **kwargs):
        pass

    chain = middleware(second_mw)(first_mw)
    assert isinstance(chain, MiddlewareChain)
    assert [mw.fn for mw in chain.collection] == [first_mw, second_mw]


@pytest.mark.asyncio
async def test_decorator_with_inner_chain():
    async def first_mw(*args, ctx, next, **kwargs):
        pass

    async def second_mw(*args, ctx, next, **kwargs):
        pass

    async def third_mw(*args, ctx, next, **kwargs):
        pass

    inner_chain = chain_of([first_mw, second_mw])
    chain = middleware(third_mw)(inner_chain)

    assert isinstance(chain, MiddlewareChain)
    assert chain == inner_chain
    assert [mw.fn for mw in chain.collection] == [first_mw, second_mw, third_mw]
