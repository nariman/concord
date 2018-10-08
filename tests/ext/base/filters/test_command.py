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
from hugo.core.middleware import (
    MiddlewareState,
    chain_of,
    is_successful_result as isr,
    middleware as m,
)
from hugo.core.utils import empty_next_callable
from hugo.ext.base.filters.command import Command, CommandContextState

from tests.helpers import make_discord_object


@pytest.mark.asyncio
async def test_simple_command(client):
    event = EventType.MESSAGE
    content = "   StAtuS the rest should be ignored"
    context = Context(
        client, event, message=make_discord_object(0, content=content)
    )

    c = Command("status")
    assert isr(await c.run(ctx=context, next=empty_next_callable))


@pytest.mark.asyncio
async def test_context_is_restored_after_processing(client):
    event = EventType.MESSAGE
    content = "   StAtuS the rest should be ignored"
    context = Context(
        client, event, message=make_discord_object(0, content=content)
    )

    @m(Command("status"))
    async def mw(*args, ctx, next, **kwargs):
        state = MiddlewareState.get_state(ctx, CommandContextState)
        assert state is not None
        assert state.last_position > 0

    assert isr(await mw.run(ctx=context, next=empty_next_callable))

    # We save the context state, but restore last position number
    state = MiddlewareState.get_state(context, CommandContextState)
    assert state is not None
    assert state.last_position == 0


@pytest.mark.asyncio
async def test_simple_command_with_pattern(client):
    event = EventType.MESSAGE
    content = "status   42 and firework the rest should be ignored"
    pattern = r"(?P<first>\w+) and (?P<second>\w+)"
    context = Context(
        client, event, message=make_discord_object(0, content=content)
    )

    @m(Command("status", rest_pattern=pattern))
    async def mw(*args, ctx, next, first, second, **kwargs):
        assert first == "42"
        assert second == "firework"

    assert isr(await mw.run(ctx=context, next=empty_next_callable))


@pytest.mark.asyncio
async def test_simple_command_with_pattern_ignores_unnamed(client):
    event = EventType.MESSAGE
    content = "status 42 and firework the rest should be ignored"
    pattern = r"(\w+) and (?P<first>\w+)"
    context = Context(
        client, event, message=make_discord_object(0, content=content)
    )

    @m(Command("status", rest_pattern=pattern))
    async def mw(*args, ctx, next, first, **kwargs):
        assert first == "firework"

    assert isr(await mw.run(ctx=context, next=empty_next_callable))


@pytest.mark.asyncio
async def test_ignoring(client):
    event = EventType.MESSAGE
    content = "prefix status the rest should be ignored"
    context = Context(
        client, event, message=make_discord_object(0, content=content)
    )

    c = Command("status")
    assert not isr(await c.run(ctx=context, next=empty_next_callable))


@pytest.mark.asyncio
async def test_ignoring_by_pattern(client):
    event = EventType.MESSAGE
    content = "status matched the rest should be ignored"
    pattern = r"unmatched"
    context = Context(
        client, event, message=make_discord_object(0, content=content)
    )

    c = Command("status", rest_pattern=pattern)
    assert not isr(await c.run(ctx=context, next=empty_next_callable))


@pytest.mark.asyncio
async def test_command_nesting(client):
    event = EventType.MESSAGE
    content = "first    second the rest should be ignored"
    context = Context(
        client, event, message=make_discord_object(0, content=content)
    )

    c = chain_of([Command("second"), Command("first")])
    assert isr(await c.run(ctx=context, next=empty_next_callable))


@pytest.mark.asyncio
async def test_command_nesting_for_prefix(client):
    event = EventType.MESSAGE
    content = "prefixstatus the rest should be ignored"
    context = Context(
        client, event, message=make_discord_object(0, content=content)
    )

    c = chain_of([Command("status"), Command("prefix", prefix=True)])
    assert isr(await c.run(ctx=context, next=empty_next_callable))


@pytest.mark.asyncio
async def test_command_nesting_ignoring(client):
    event = EventType.MESSAGE
    content = "first unmatched the rest should be ignored"
    context = Context(
        client, event, message=make_discord_object(0, content=content)
    )

    c = chain_of([Command("second"), Command("first")])
    assert not isr(await c.run(ctx=context, next=empty_next_callable))
