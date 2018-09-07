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

from hugo import handler
from hugo import middleware
from hugo.client import Client
from hugo.constants import EventType
from hugo.context import Context


class TestEventNormalization:
    @pytest.mark.asyncio
    async def test_without_positional(self, client_instance):
        args = [1, "2", [1, "2"]]
        kwargs = {"before": 1, "after": "2", "other": [1, "2"]}
        en = handler.EventNormalization()
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
        en = handler.EventNormalization()
        event = EventType.MESSAGE_EDIT
        event_parameters = handler.EventNormalization.EVENTS[event]

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
        ec = handler.EventConstraint(EventType.MESSAGE)

        assert not middleware.Middleware.is_successful_result(
            await ec.run(
                ctx=Context(client_instance, event),
                next=Client.default_next_callable,
            )
        )

    @pytest.mark.asyncio
    async def test_passing(self, client_instance):
        event = EventType.MESSAGE
        ec = handler.EventConstraint(EventType.MESSAGE)

        assert middleware.Middleware.is_successful_result(
            await ec.run(
                ctx=Context(client_instance, event),
                next=Client.default_next_callable,
            )
        )

    def test_decorator(self):
        event = EventType.MESSAGE
        ec = handler.event(event)(Client.default_next_callable)

        assert isinstance(ec, middleware.MiddlewareChain)
        assert isinstance(ec.collection[-1], handler.EventConstraint)
        assert ec.collection[-1].event == event
