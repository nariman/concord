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

from hugo.core.middleware import MiddlewareState


@pytest.mark.asyncio
async def test_running_behaviour_on_defaults(context, sample_parameters):
    sa, skwa = sample_parameters

    class State:
        pass

    state = State()
    ms = MiddlewareState(state)

    async def next(*args, ctx, **kwargs):
        assert ctx == context and list(args) == sa and kwargs == skwa
        assert hasattr(ctx, "states")
        assert ctx.states.get(State) == state
        assert MiddlewareState.get_state(ctx, State) == state
        return 42

    assert await ms.run(*sa, ctx=context, next=next, **skwa) == 42


@pytest.mark.asyncio
async def test_running_behaviour_with_key(context, sample_parameters):
    sa, skwa = sample_parameters

    class State:
        pass

    state = State()
    ms = MiddlewareState(state, key="my_state")

    async def next(*args, ctx, my_state, **kwargs):
        assert ctx == context and list(args) == sa and kwargs == skwa
        assert hasattr(ctx, "states")
        assert ctx.states.get(State) == state
        assert MiddlewareState.get_state(ctx, State) == state
        assert my_state == state
        return 42

    assert await ms.run(*sa, ctx=context, next=next, **skwa) == 42


@pytest.mark.asyncio
async def test_running_behaviour_with_context_state(context, sample_parameters):
    sa, skwa = sample_parameters

    class ContextState(MiddlewareState.ContextState):
        pass

    ms = MiddlewareState(ContextState)

    async def next(*args, ctx, **kwargs):
        assert ctx == context and list(args) == sa and kwargs == skwa
        assert isinstance(
            MiddlewareState.get_state(ctx, ContextState), ContextState
        )
        return 42

    assert await ms.run(*sa, ctx=context, next=next, **skwa) == 42
