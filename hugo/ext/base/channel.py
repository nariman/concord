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

import discord

from hugo.core.context import Context
from hugo.core.middleware import Middleware, MiddlewareResult


class ChannelType(Middleware):
    """Message context filter.

    The message should be sent in the given channel types to invoke the next
    middleware.

    TODO: Work with different event types.

    Attributes
    ----------
    guild : bool
        Is the channel should be a guild channel.
    private : bool
        Is the channel should be a private channel (DM or group).
    text : bool
        Is the channel should be a guild text channel.
    voice : bool
        Is the channel should be a guild voice channel.
    dm : bool
        Is the channel should be a private DM channel.
    group : bool
        Is the channel should be a private group channel.
    """

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
        self.text = guild or text
        self.voice = guild or voice
        self.dm = private or dm
        self.group = private or group

    async def run(self, *args, ctx: Context, next, **kwargs):  # noqa: D102
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
