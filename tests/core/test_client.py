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

import asyncio

import discord
import pytest

from concord.client import Client, create_client
from concord.constants import EventType
from concord.extension import Extension
from concord.middleware import as_middleware


@pytest.mark.asyncio
async def test_event_dispatching(event_loop, sample_parameters):
    sa, skwa = sample_parameters
    event = "message"
    result = asyncio.Event()

    class SomeExtension(Extension):
        @property
        def extension_middleware(self):
            @as_middleware
            async def mw(*args, ctx, next, **kwargs):
                assert ctx.event == EventType(event)
                assert ctx.args == sa
                assert ctx.kwargs == skwa
                result.set()

            return [mw]

    client = Client()
    client.extension_manager.register_extension(SomeExtension)
    client.dispatch(event, *sa, **skwa)
    assert await asyncio.wait_for(result.wait(), timeout=1.0)
    await client.close()


@pytest.mark.asyncio
async def test_unknown_event_dispatching(event_loop):
    event = "firework!"
    result = asyncio.Event()

    class SomeExtension(Extension):
        @property
        def extension_middleware(self):
            @as_middleware
            async def mw(*args, ctx, next, **kwargs):
                assert ctx.event == EventType.UNKNOWN
                result.set()

            return [mw]

    client = Client()
    client.extension_manager.register_extension(SomeExtension)
    client.dispatch(event)
    assert await asyncio.wait_for(result.wait(), timeout=1.0)
    await client.close()


def test_custom_client_creation():
    class CustomClient(discord.Client):
        pass

    classes_to_test_on = [discord.AutoShardedClient, CustomClient]

    for klass in classes_to_test_on:
        instance = create_client(klass)
        assert isinstance(instance, Client) and isinstance(instance, klass)
