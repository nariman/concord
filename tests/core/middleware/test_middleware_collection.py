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

from concord.middleware import (
    Middleware,
    MiddlewareCollection,
    as_middleware,
    collection_of,
)


@pytest.mark.asyncio
async def test_class_is_abstract():
    class Collection(MiddlewareCollection):
        pass

    class ImplementedCollection(MiddlewareCollection):
        async def run(self, *args, ctx, next, **kwargs):
            pass

    with pytest.raises(TypeError):
        Collection()
    with pytest.raises(TypeError):
        instance = ImplementedCollection()
        await instance()


def test_middleware_addition():
    class Collection(MiddlewareCollection):
        async def run(self, *args, ctx, next, **kwargs):
            pass

    @as_middleware
    async def first_mw(*args, ctx, next, **kwargs):
        pass

    @as_middleware
    async def second_mw(*args, ctx, next, **kwargs):
        pass

    mc = Collection()
    mc.add_middleware(first_mw)
    mc.add_middleware(second_mw)

    assert mc.collection == [first_mw, second_mw]


def test_middleware_addition_constraints():
    class Collection(MiddlewareCollection):
        async def run(self, *args, ctx, next, **kwargs):
            pass

    async def mw(*args, ctx, next, **kwargs):
        pass

    mc = Collection()

    with pytest.raises(ValueError):
        mc.add_middleware(mw)
    with pytest.raises(ValueError):
        mc.add_middleware(42)


def test_helper():
    class Collection(MiddlewareCollection):
        async def run(self, *args, ctx, next, **kwargs):
            pass

    async def first_mw(*args, ctx, next, **kwargs):
        pass

    @as_middleware
    async def second_mw(*args, ctx, next, **kwargs):
        pass

    mc = collection_of(Collection, [first_mw, second_mw])

    assert isinstance(mc, Collection)
    for mw in mc.collection:
        assert isinstance(mw, Middleware)
    assert [mw.fn for mw in mc.collection] == [first_mw, second_mw.fn]
