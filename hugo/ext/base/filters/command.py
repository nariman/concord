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
from typing import Any, Callable, Optional, Union

from hugo.core.context import Context
from hugo.core.middleware import Middleware, MiddlewareResult, MiddlewareState


class CommandContextState(MiddlewareState.ContextState):
    """State with information about already processed parts of a message.

    Attributes
    ----------
    last_position : int
        Position in a message string where last match has found and processed.
    """

    def __init__(self):
        self.last_position = 0


class Command(Middleware):
    """Message context filter.

    Attributes
    ----------
    name : str
        Command name that should be present in a message.
    prefix : bool
        Allow command name to be a prefix of the full word (full command name).
        Useful for global command prefix.
    rest_pattern : Optional[str]
        The regex string to process the rest part of a message.
    """

    def __init__(
        self,
        name: str,
        *,
        prefix: bool = False,
        rest_pattern: Optional[str] = None,
    ):
        super().__init__()
        self.name = name
        self.prefix = prefix
        self.rest_pattern = rest_pattern

    @staticmethod
    def _get_state(ctx: Context) -> CommandContextState:
        state = MiddlewareState.get_state(ctx, CommandContextState)

        if state is None:
            state = CommandContextState()
            MiddlewareState.set_state(ctx, state)
        #
        return state

    # TODO: Method to rewrite. It looks awful.
    # TODO: What about arabic text?
    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:  # noqa: D102
        state = self._get_state(ctx)
        message = ctx.kwargs["message"]
        name_pattern = rf"{self.name}" if self.prefix else rf"{self.name}\b"

        # We should care about whitespaces on the start and do not forget to
        # count this into state.
        # fmt: off
        message_part = message.content[state.last_position:]
        message_part_clean = message_part.lstrip()
        state.last_position += len(message_part) - len(message_part_clean)
        # fmt: on

        result = re.match(name_pattern, message_part_clean, re.I)

        if not result:
            return MiddlewareResult.IGNORE
        #
        state.last_position += result.end()

        if self.rest_pattern:
            # fmt: off
            message_part = message_part_clean[result.end():]
            message_part_clean = message_part.lstrip()
            state.last_position += len(message_part) - len(message_part_clean)
            # fmt: on

            result = re.match(self.rest_pattern, message_part_clean)

            if result:
                kwargs.update(result.groupdict())
                state.last_position += result.end()
            else:
                return MiddlewareResult.IGNORE
        #
        return await next(*args, ctx=ctx, **kwargs)
