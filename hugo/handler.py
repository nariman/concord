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

import discord

from .context import Context
from .middleware import Middleware, MiddlewareResult, middleware


class Pattern(Middleware):
    """Message context filter.

    The message should match the given regex pattern to invoke the next
    middleware.

    Only named subgroups will be passed to the next middleware.

    Attributes
    ----------
    pattern : str
        The source regex string.
    """

    def __init__(self, pattern: str):
        self.pattern = pattern

    async def run(self, *args, ctx: Context, next, **kwargs):
        result = re.search(self.pattern, ctx.message.content)

        if result:
            kwargs.update(result.groupdict())
            return await next(*args, ctx=ctx, **kwargs)
        return MiddlewareResult.IGNORE


def pattern(pattern: str):
    """Append a :class:`Pattern` middleware to the chain.

    Parameters
    ----------
    pattern : str
        The source regex string.
    """
    return middleware(Pattern(pattern))


class BotConstraint(Middleware):
    """Message context filter.

    The message should be authored by or not authored by a real user to invoke
    the next middleware.

    Attributes
    ----------
    authored_by_bot : bool
        Is the message should be authored by bot or not.
    """

    def __init__(self, *, authored_by_bot: bool):
        self.authored_by_bot = authored_by_bot

    async def run(self, *args, ctx: Context, next, **kwargs):
        if not self.authored_by_bot ^ ctx.message.author.bot:
            return await next(*args, ctx=ctx, **kwargs)
        return MiddlewareResult.IGNORE


def not_authored_by_bot():
    """Append a :class:`BotConstraint` middleware to the chain with a "not
    authored by bot" constraint.
    """
    return middleware(BotConstraint(authored_by_bot=False))


def authored_by_bot():
    """Append a :class:`BotConstraint` middleware to the chain with a "authored
    by bot" constraint.
    """
    return middleware(BotConstraint(authored_by_bot=True))


class ChannelType(Middleware):
    """Message context filter.

    The message should be sent in the given channel types to invoke the next
    middleware.
    """

    def __init__(
        self,
        *,
        guild: bool = False,
        private: bool = False,
        text: bool = False,
        # voice: bool = False,
        dm: bool = False,
        group: bool = False,
    ):
        self.text = guild or text
        # self.voice = guild or voice
        self.dm = private or dm
        self.group = private or group

    async def run(self, *args, ctx: Context, next, **kwargs):
        channel = ctx.message.channel

        # fmt: off
        if (
            self.text and isinstance(channel, discord.TextChannel)
            # or self.voice and isinstance(channel, discord.VoiceChannel)
            or self.dm and isinstance(channel, discord.DMChannel)
            or self.group and isinstance(channel, discord.GroupChannel)
        ):
            return await next(*args, ctx=ctx, **kwargs)
        # fmt: on

        return MiddlewareResult.IGNORE


def channel_type(
    *,
    guild: bool = False,
    private: bool = False,
    text: bool = False,
    # voice: bool = False,
    dm: bool = False,
    group: bool = False,
):
    """Append a :class:`ChannelType` middleware to the chain with given
    constraints.
    """
    return middleware(
        ChannelType(
            guild=guild,
            private=private,
            text=text,
            # voice=voice,
            dm=dm,
            group=group,
        )
    )
