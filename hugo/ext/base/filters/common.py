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

import re
from typing import Any, Callable, Union

import discord

from hugo.core.constants import EventType
from hugo.core.context import Context
from hugo.core.middleware import Middleware, MiddlewareResult


class EventTypeFilter(Middleware):
    """Event type filter.

    Args:
        event: Event type to allow.

    Attributes:
        event: Event type to allow.
    """

    event: EventType

    def __init__(self, event: EventType):
        super().__init__()
        self.event = event

    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:  # noqa: D102
        if ctx.event == self.event:
            return await next(*args, ctx=ctx, **kwargs)
        return MiddlewareResult.IGNORE


class PatternFilter(Middleware):
    """Message context filter.

    The message should match the given regex pattern to invoke the next
    middleware.

    Only named subgroups will be passed to the next middleware.

    TODO: Work with different event types.

    Args:
        pattern: The source regex string.

    Attributes:
        pattern: The source regex string.
    """

    pattern: str

    def __init__(self, pattern: str):
        super().__init__()
        self.pattern = pattern

    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:  # noqa: D102
        result = re.search(self.pattern, ctx.kwargs["message"].content)

        if result:
            kwargs.update(result.groupdict())
            return await next(*args, ctx=ctx, **kwargs)
        #
        return MiddlewareResult.IGNORE


class BotFilter(Middleware):
    """Message context filter.

    The message should be authored by or not authored by a real user to invoke
    the next middleware.

    Args:
        authored_by_bot: Is the message should be authored by bot or not.

    Attributes:
        authored_by_bot: Is the message should be authored by bot or not.
    """

    authored_by_bot: bool

    def __init__(self, *, authored_by_bot: bool):
        super().__init__()
        self.authored_by_bot = authored_by_bot

    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:  # noqa: D102
        if not self.authored_by_bot ^ ctx.kwargs["message"].author.bot:
            return await next(*args, ctx=ctx, **kwargs)
        return MiddlewareResult.IGNORE


class ChannelTypeFilter(Middleware):
    """Message context filter.

    The message should be sent in the given channel types to invoke the next
    middleware.

    TODO: Work with different event types.

    Args:
        guild: Is the channel should be a guild channel.
        private: Is the channel should be a private channel (DM or group).
        text: Is the channel should be a guild text channel.
        voice: Is the channel should be a guild voice channel.
        dm: Is the channel should be a private DM channel.
        group: Is the channel should be a private group channel.

    Attributes:
        guild: Is the channel should be a guild channel.
        private: Is the channel should be a private channel (DM or group).
        text: Is the channel should be a guild text channel.
        voice: Is the channel should be a guild voice channel.
        dm: Is the channel should be a private DM channel.
        group: Is the channel should be a private group channel.
    """

    guild: bool
    private: bool
    text: bool
    voice: bool
    dm: bool
    group: bool

    def __init__(
        self,
        *,
        guild: bool = False,
        private: bool = False,
        text: bool = False,
        voice: bool = False,
        dm: bool = False,
        group: bool = False,
    ):
        super().__init__()
        self.text = guild or text
        self.voice = guild or voice
        self.dm = private or dm
        self.group = private or group

    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:  # noqa: D102
        channel = ctx.kwargs["message"].channel

        # fmt: off
        if (
            self.text and isinstance(channel, discord.TextChannel)
            or self.voice and isinstance(channel, discord.VoiceChannel)
            or self.dm and isinstance(channel, discord.DMChannel)
            or self.group and isinstance(channel, discord.GroupChannel)
        ):
            return await next(*args, ctx=ctx, **kwargs)
        # fmt: on

        return MiddlewareResult.IGNORE
