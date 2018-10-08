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

import pytest

from hugo.core.constants import EventType
from hugo.core.context import Context
from hugo.core.middleware import is_successful_result as isr
from hugo.core.utils import empty_next_callable
from hugo.ext.base.filters.common import BotFilter

from tests.helpers import make_discord_object


@pytest.mark.parametrize("authored_by_bot", [True, False])
@pytest.mark.parametrize("bot", [True, False])
@pytest.mark.asyncio
async def test(client, authored_by_bot, bot):
    event = EventType.MESSAGE
    context = Context(
        client,
        event,
        message=make_discord_object(0, author=make_discord_object(1, bot=bot)),
    )

    bf = BotFilter(authored_by_bot=authored_by_bot)

    if not authored_by_bot ^ bot:
        assert isr(await bf.run(ctx=context, next=empty_next_callable))
    else:
        assert not isr(await bf.run(ctx=context, next=empty_next_callable))
