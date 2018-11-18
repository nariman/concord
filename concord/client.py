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

import logging
from typing import Type

import discord

from concord.constants import EventType
from concord.context import Context
from concord.extension import Manager
from concord.utils import empty_next_callable


log = logging.getLogger(__name__)


class Client(discord.Client):
    """Wrapper around default discord.py library client.

    Attributes:
        extension_manager: Extension manager instance associated with this
            client.
    """

    extension_manager: Manager

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension_manager = Manager()

        log.info("Concord client initialized")

    def dispatch(self, event: str, *args, **kwargs):  # noqa: D401
        """Wrapper around default event dispatcher for a client."""
        super().dispatch(event, *args, **kwargs)

        try:
            event_type = EventType(event)
        except ValueError:
            event_type = EventType.UNKNOWN
        #
        ctx = Context(self, event_type, *args, **kwargs)
        log.debug(f"Dispatching event `{event_type}`")

        self.loop.create_task(
            self._run_event(
                self.extension_manager.run,
                event,
                ctx=ctx,
                next=empty_next_callable,
            )
        )


def create_client(client: Type[discord.Client]):
    """Get an instance of client.

    It returns an instance of subclass, that is based on your provided class and
    a wrapper class. It's needed to add some specific functionality into client
    in order to be able to process events.

    Args:
        client: Client class to base on.
    """

    class MixedClient(Client, client):
        pass

    return MixedClient()
