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

from hugo.core.constants import EventType
from hugo.core.context import Context
from hugo.ext.base.event import EventNormalization


@pytest.mark.asyncio
async def test_without_positional(client):
    sa, skwa = [1, "2", [1, "2"]], {"other": [1, "2"]}

    en = EventNormalization()
    event = EventType.READY

    async def check(*args, ctx, **kwargs):
        assert len(ctx.args) == len(sa)
        assert len(ctx.kwargs) == len(skwa)

    await en.run(ctx=Context(client, event, *sa, **skwa), next=check)


@pytest.mark.asyncio
async def test_with_positional(client):
    sa, skwa = [1, "2", [1, "2"]], {"other": [1, "2"]}

    en = EventNormalization()
    event = EventType.MESSAGE_EDIT
    context = Context(client, event, *sa, **skwa)
    event_fields = EventNormalization.EVENT_FIELDS[event]

    async def check(*args, ctx, **kwargs):
        assert len(ctx.args) == len(sa)
        assert len(ctx.kwargs) - len(event_fields) == len(skwa)

        for i, k in enumerate(event_fields):
            assert ctx.kwargs[k] == sa[i]

    await en.run(ctx=context, next=check)
    # Test one more time, it should process as well
    await en.run(ctx=context, next=check)


@pytest.mark.asyncio
async def test_unknown(client):
    sa, skwa = [1, "2", [1, "2"]], {"other": [1, "2"]}

    en = EventNormalization()
    event = EventType.UNKNOWN

    async def check(*args, ctx, **kwargs):
        assert len(ctx.args) == len(sa)
        assert len(ctx.kwargs) == len(skwa)

    await en.run(ctx=Context(client, event, *sa, **skwa), next=check)
