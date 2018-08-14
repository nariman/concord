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

    async def run(self, ctx: Context, next, *args, **kwargs):
        result = re.search(self.pattern, ctx.message.content)

        if result:
            kwargs.update(result.groupdict())
            return await next(ctx, *args, **kwargs)
        return MiddlewareResult.IGNORE


def pattern(pattern: str):
    """Append a :class:`Pattern` middleware to the chain.

    Parameters
    ----------
    pattern : str
        The source regex string.
    """
    outer_middleware = Pattern(pattern)

    def decorator(inner_middleware: Middleware):
        return middleware(outer_middleware)(inner_middleware)

    return decorator
