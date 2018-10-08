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
    MiddlewareResult,
    MiddlewareSequence,
    collection_of,
    sequence_of,
)
from hugo.core.utils import empty_next_callable


# We use `collection_of` instead of direct instance of `MiddlewareSequence`
# because we assume that `collection_of` has tested and ok to use and due to the
# same logic under the hood of `collection_of`.


@pytest.mark.asyncio
async def test_running_behaviour(context, sample_parameters):
    sa, skwa = sample_parameters

    async def first_mw(*args, ctx, next, **kwargs):
        return MiddlewareResult.IGNORE

    async def second_mw(*args, ctx, next, **kwargs):
        return 2

    ooa = collection_of(MiddlewareSequence, [first_mw, second_mw])
    assert await ooa.run(
        *sa, ctx=context, next=empty_next_callable, **skwa
    ) == (MiddlewareResult.IGNORE, 2)


@pytest.mark.asyncio
async def test_running_behaviour_on_ignoring(context, sample_parameters):
    sa, skwa = sample_parameters

    async def first_mw(*args, ctx, next, **kwargs):
        return MiddlewareResult.IGNORE

    async def second_mw(*args, ctx, next, **kwargs):
        return MiddlewareResult.IGNORE

    ooa = collection_of(MiddlewareSequence, [first_mw, second_mw])
    assert (
        await ooa.run(*sa, ctx=context, next=empty_next_callable, **skwa)
        == MiddlewareResult.IGNORE
    )


def test_helper():
    async def first_mw(*args, ctx, next, **kwargs):
        pass

    async def second_mw(*args, ctx, next, **kwargs):
        pass

    chain = sequence_of([first_mw, second_mw])
    # Just check that, `collection_of` covers all of the other stuff to check.
    assert isinstance(chain, MiddlewareSequence)
