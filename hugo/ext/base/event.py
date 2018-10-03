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

from typing import Any, Union

from hugo.core.constants import EventType
from hugo.core.context import Context
from hugo.core.middleware import Middleware, MiddlewareResult, MiddlewareState


class EventNormalizationContextState(MiddlewareState.ContextState):
    """State with information about already processed event normalization.

    Attributes:
        is_processed: Is normalization has been applied.
    """

    def __init__(self):
        self.is_processed = False


class EventNormalization(Middleware):
    """Event parameters normalization.

    A middleware for converting positional parameters into keyword for known
    events.
    """

    EVENTS = {
        EventType.CONNECT: tuple(),
        EventType.READY: tuple(),
        EventType.SHARD_READY: ("shard_id",),
        EventType.RESUMED: tuple(),
        EventType.ERROR: tuple(),
        EventType.SOCKET_RAW_RECEIVE: ("msg",),
        EventType.SOCKET_RAW_SEND: ("payload",),
        EventType.TYPING: ("channel", "user", "when"),
        EventType.MESSAGE: ("message",),
        EventType.MESSAGE_DELETE: ("message",),
        EventType.RAW_MESSAGE_DELETE: ("payload",),
        EventType.RAW_BULK_MESSAGE_DELETE: ("payload",),
        EventType.MESSAGE_EDIT: ("before", "after"),
        EventType.RAW_MESSAGE_EDIT: ("payload",),
        EventType.REACTION_ADD: ("reaction", "user"),
        EventType.RAW_REACTION_ADD: ("payload",),
        EventType.REACTION_REMOVE: ("reaction, user",),
        EventType.RAW_REACTION_REMOVE: ("payload",),
        EventType.REACTION_CLEAR: ("message", "reactions"),
        EventType.RAW_REACTION_CLEAR: ("payload",),
        EventType.PRIVATE_CHANNEL_CREATE: ("channel",),
        EventType.PRIVATE_CHANNEL_DELETE: ("channel",),
        EventType.PRIVATE_CHANNEL_UPDATE: ("before", "after"),
        EventType.PRIVATE_CHANNEL_PINS_UPDATE: ("channel", "last_pin"),
        EventType.GUILD_CHANNEL_CREATE: ("channel",),
        EventType.GUILD_CHANNEL_DELETE: ("channel",),
        EventType.GUILD_CHANNEL_UPDATE: ("before", "after"),
        EventType.GUILD_CHANNEL_PINS_UPDATE: ("channel", "last_pin"),
        EventType.MEMBER_JOIN: ("member",),
        EventType.MEMBER_REMOVE: ("member",),
        EventType.MEMBER_UPDATE: ("before", "after"),
        EventType.GUILD_JOIN: ("guild",),
        EventType.GUILD_REMOVE: ("guild",),
        EventType.GUILD_UPDATE: ("before", "after"),
        EventType.GUILD_ROLE_CREATE: ("role",),
        EventType.GUILD_ROLE_DELETE: ("role",),
        EventType.GUILD_ROLE_UPDATE: ("before", "after"),
        EventType.GUILD_EMOJIS_UPDATE: ("guild", "before", "after"),
        EventType.GUILD_AVAILABLE: ("guild",),
        EventType.GUILD_UNAVAILABLE: ("guild",),
        EventType.VOICE_STATE_UPDATE: ("member", "before", "after"),
        EventType.MEMBER_BAN: ("guild", "user"),
        EventType.MEMBER_UNBAN: ("guild", "user"),
        EventType.GROUP_JOIN: ("channel", "user"),
        EventType.GROUP_REMOVE: ("channel", "user"),
        EventType.RELATIONSHIP_ADD: ("relationship",),
        EventType.RELATIONSHIP_REMOVE: ("relationship",),
        EventType.RELATIONSHIP_UPDATE: ("before", "after"),
    }

    @staticmethod
    def _get_state(ctx: Context) -> EventNormalizationContextState:
        state = MiddlewareState.get_state(ctx, EventNormalizationContextState)

        if state is None:
            state = EventNormalizationContextState()
            MiddlewareState.set_state(ctx, state)
        #
        return state

    async def run(
        self, *args, ctx: Context, next, **kwargs
    ) -> Union[MiddlewareResult, Any]:  # noqa: D102
        if ctx.event not in self.EVENTS:
            return await next(*args, ctx=ctx, **kwargs)

        state = self._get_state(ctx)
        if state.is_processed:
            return await next(*args, ctx=ctx, **kwargs)

        for i, parameter in enumerate(self.EVENTS[ctx.event]):
            ctx.kwargs[parameter] = ctx.args[i]
        plen = len(self.EVENTS[ctx.event])
        ctx.args = ctx.args[plen:]

        state.is_processed = True
        return await next(*args, ctx=ctx, **kwargs)
