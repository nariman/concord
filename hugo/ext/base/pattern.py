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

from hugo.core.context import Context
from hugo.core.middleware import Middleware, MiddlewareResult


class Pattern(Middleware):
    """Message context filter.

    The message should match the given regex pattern to invoke the next
    middleware.

    Only named subgroups will be passed to the next middleware.

    TODO: Work with different event types.

    Attributes
    ----------
    pattern : str
        The source regex string.
    """

    def __init__(self, pattern: str):
        self.pattern = pattern

    async def run(self, *args, ctx: Context, next, **kwargs):  # noqa: D102
        result = re.search(self.pattern, ctx.kwargs["message"].content)

        if result:
            kwargs.update(result.groupdict())
            return await next(*args, ctx=ctx, **kwargs)
        #
        return MiddlewareResult.IGNORE
