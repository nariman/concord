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

from hugo.core.constants import EventType


class Context:
    """Event processing context.

    Parameters
    ----------
    client : :class:`discord.Client`
        A discord.py client instance.
    event : :class:`.constants.EventType`
        Event's type context is creating for.

    Attributes
    ----------
    client : :class:`discord.Client`
        A discord.py client instance.
    event : :class:`.constants.EventType`
        Event's type context is created for.
    args : list
        Unnamed / positional arguments, which was provided with event.
    kargs : dict
        Keyword arguments, which was provided with event.
    """

    def __init__(
        self, client: discord.Client, event: EventType, *args, **kwargs
    ):
        self.client = client
        self.event = event
        self.args = list(args)
        self.kwargs = kwargs
