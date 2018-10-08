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

from typing import Any, Callable, Union, Dict, Tuple

from concord.constants import EventType
from concord.context import Context
from concord.middleware import Middleware, MiddlewareResult, MiddlewareState


class EventNormalizationContextState(MiddlewareState.ContextState):
    """State with information about already processed event normalization.

    Attributes:
        is_processed: Is normalization has been applied.
    """

    is_processed: bool

    def __init__(self):
        self.is_processed = False


class EventNormalization(Middleware):
    """Event parameters normalization.

    A middleware for parsing positional event' fields into keyword for known
    events. Positional fields will be left as is.

    Attributes:
        EVENT_FIELDS: Fields list each event has.
    """

    EVENT_FIELDS: Dict[EventType, Tuple[str, ...]] = {
        EventType.CONNECT: tuple(),
        EventType.ERROR: tuple(),
        EventType.GROUP_JOIN: ("channel", "user"),
        EventType.GROUP_REMOVE: ("channel", "user"),
        EventType.GUILD_AVAILABLE: ("guild",),
        EventType.GUILD_CHANNEL_CREATE: ("channel",),
        EventType.GUILD_CHANNEL_DELETE: ("channel",),
        EventType.GUILD_CHANNEL_PINS_UPDATE: ("channel", "last_pin"),
        EventType.GUILD_CHANNEL_UPDATE: ("before", "after"),
        EventType.GUILD_EMOJIS_UPDATE: ("guild", "before", "after"),
        EventType.GUILD_JOIN: ("guild",),
        EventType.GUILD_REMOVE: ("guild",),
        EventType.GUILD_ROLE_CREATE: ("role",),
        EventType.GUILD_ROLE_DELETE: ("role",),
        EventType.GUILD_ROLE_UPDATE: ("before", "after"),
        EventType.GUILD_UNAVAILABLE: ("guild",),
        EventType.GUILD_UPDATE: ("before", "after"),
        EventType.MEMBER_BAN: ("guild", "user"),
        EventType.MEMBER_JOIN: ("member",),
        EventType.MEMBER_REMOVE: ("member",),
        EventType.MEMBER_UNBAN: ("guild", "user"),
        EventType.MEMBER_UPDATE: ("before", "after"),
        EventType.MESSAGE: ("message",),
        EventType.MESSAGE_DELETE: ("message",),
        EventType.MESSAGE_EDIT: ("before", "after"),
        EventType.PRIVATE_CHANNEL_CREATE: ("channel",),
        EventType.PRIVATE_CHANNEL_DELETE: ("channel",),
        EventType.PRIVATE_CHANNEL_PINS_UPDATE: ("channel", "last_pin"),
        EventType.PRIVATE_CHANNEL_UPDATE: ("before", "after"),
        EventType.RAW_BULK_MESSAGE_DELETE: ("payload",),
        EventType.RAW_MESSAGE_DELETE: ("payload",),
        EventType.RAW_MESSAGE_EDIT: ("payload",),
        EventType.RAW_REACTION_ADD: ("payload",),
        EventType.RAW_REACTION_CLEAR: ("payload",),
        EventType.RAW_REACTION_REMOVE: ("payload",),
        EventType.REACTION_ADD: ("reaction", "user"),
        EventType.REACTION_CLEAR: ("message", "reactions"),
        EventType.REACTION_REMOVE: ("reaction, user",),
        EventType.READY: tuple(),
        EventType.RELATIONSHIP_ADD: ("relationship",),
        EventType.RELATIONSHIP_REMOVE: ("relationship",),
        EventType.RELATIONSHIP_UPDATE: ("before", "after"),
        EventType.RESUMED: tuple(),
        EventType.SHARD_READY: ("shard_id",),
        EventType.SOCKET_RAW_RECEIVE: ("msg",),
        EventType.SOCKET_RAW_SEND: ("payload",),
        EventType.SOCKET_RESPONSE: ("playload",),
        EventType.TYPING: ("channel", "user", "timestamp"),
        EventType.VOICE_STATE_UPDATE: ("member", "before", "after"),
        EventType.WEBHOOKS_UPDATE: ("channel",),
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
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:  # noqa: D102
        if ctx.event not in self.EVENT_FIELDS:
            return await next(*args, ctx=ctx, **kwargs)

        state = self._get_state(ctx)
        if state.is_processed:
            return await next(*args, ctx=ctx, **kwargs)

        for i, parameter in enumerate(self.EVENT_FIELDS[ctx.event]):
            ctx.kwargs[parameter] = ctx.args[i]

        state.is_processed = True
        return await next(*args, ctx=ctx, **kwargs)
