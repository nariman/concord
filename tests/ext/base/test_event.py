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
from hugo.core.client import Client
from hugo.core.constants import EventType
from hugo.core.context import Context
from hugo.ext.base.event import EventConstraint, EventNormalization


class TestEventNormalization:
    @pytest.mark.asyncio
    async def test_without_positional(self, client_instance):
        args = [1, "2", [1, "2"]]
        kwargs = {"before": 1, "after": "2", "other": [1, "2"]}
        en = EventNormalization()
        event = EventType.READY

        async def check(*_, ctx, **__):
            assert len(ctx.args) == len(args)
            assert len(ctx.kwargs) == len(kwargs)

        await en.run(
            ctx=Context(client_instance, event, *args, **kwargs), next=check
        )

    @pytest.mark.asyncio
    async def test_with_positional(self, client_instance):
        args = [1, "2", [1, "2"]]
        kwargs = {"other": [1, "2"]}
        en = EventNormalization()
        event = EventType.MESSAGE_EDIT
        event_parameters = EventNormalization.EVENTS[event]

        async def check(*_, ctx, **__):
            assert len(ctx.args) + len(event_parameters) == len(args)
            assert len(ctx.kwargs) - len(event_parameters) == len(kwargs)

            for i, k in enumerate(event_parameters):
                assert ctx.kwargs[k] == args[i]

        await en.run(
            ctx=Context(client_instance, event, *args, **kwargs), next=check
        )


class TestEventConstraint:
    @pytest.mark.asyncio
    async def test_ignoring(self, client_instance):
        event = EventType.READY
        ec = EventConstraint(EventType.MESSAGE)

        assert not middleware.Middleware.is_successful_result(
            await ec.run(
                ctx=Context(client_instance, event),
                next=Client.default_next_callable,
            )
        )

    @pytest.mark.asyncio
    async def test_passing(self, client_instance):
        event = EventType.MESSAGE
        ec = EventConstraint(EventType.MESSAGE)

        assert middleware.Middleware.is_successful_result(
            await ec.run(
                ctx=Context(client_instance, event),
                next=Client.default_next_callable,
            )
        )
