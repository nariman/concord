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

from typing import Any, Dict, List

import discord

from hugo.core.constants import EventType


class Context:
    """Event processing context.

    .. note::
        Attributes ``client`` and ``event`` are not supposed to be changed.

    Args:
        client: A discord.py client instance.
        event: Event's type context is creating for.
        *args: Unnamed / positional arguments, which was provided with event.
        **kwargs: Keyword arguments, which was provided with event.

    Attributes:
        client: A discord.py client instance.
        event: Event's type context is created for.
        args: Unnamed / positional arguments, which was provided with event.
        kwargs: Keyword arguments, which was provided with event.
    """

    client: discord.Client
    event: EventType
    args: List
    kwargs: Dict[str, Any]

    def __init__(
        self, client: discord.Client, event: EventType, *args, **kwargs
    ):
        self.client = client
        self.event = event
        self.args = list(args)
        self.kwargs = kwargs
