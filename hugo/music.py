"""
Hugo - Discord Bot

MIT License

Copyright (c) 2017 woofilee

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import random

from hugo.command import (
    Group,
    command,
    group
)
from hugo import exceptions


class Entry:
    def __init__(self, url, player):
        self.url = url
        self.player = player


class State:
    def __init__(self, bot):
        self.current: int = None
        self.playlist = []
        self.voice_client = None
        self.bot = bot
        self.next_entry_trigger = asyncio.Event()
        self.task = self.bot.loop.create_task(self.__task())

    @property
    def current_entry(self):
        if self.current is None:
            return None
        return self.playlist[self.current]

    @property
    def player(self):
        if self.current is None:
            return None
        return self.current_entry.player

    @property
    def is_playing(self):
        if self.voice_client is None or self.current is None:
            return False

        return not self.player.is_done()

    def add_entry(self, entry: Entry):
        self.playlist.append(entry)

    def remove_entry(self, entry: Entry):
        self.playlist.remove(entry)

    def next_entry(self):
        self.bot.loop.call_soon_threadsafe(self.next_entry_trigger.set)

    async def __task(self):
        while True:
            self.next_entry_trigger.clear()

            if self.current is None:
                self.current = 0
            else:
                self.current += 1

            if self.current >= len(self.playlist):
                self.current = None
            else:
                self.player.start()

            await self.next_entry_trigger.wait()


class Music(Group):
    ytdl_options = {
        "default_search": "auto",
        "quiet": True,
    }

    def __init__(self):
        super().__init__("Music", "Music related commands")
        self.states = {}

    def get_state(self, ctx):
        if ctx.message.server is not None:
            id = ctx.message.server.id
        else:
            id = ctx.message.channel.id

        if id is None:
            raise exceptions.BotException

        state = self.states.get(id)
        if state is None:
            state = State(ctx.bot)
            self.states[id] = state
        return state

    @command(slug="join",
             templates=[
                 r"join",
             ],
             short_description="Join to your voice channel",
             long_description="")
    async def join(self, ctx):
        channel = ctx.message.author.voice_channel
        if channel is None:
            await ctx.bot.send_message(ctx.message.channel,
                                       "You're not in a voice channel.")
            return

        state = self.get_state(ctx)
        if state.voice_client is None:
            state.voice_client = await ctx.bot.join_voice_channel(channel)
        else:
            await state.voice_client.move_to(channel)

    @command(slug="leave",
             templates=[
                 r"leave",
             ],
             short_description="Leave voice channel",
             long_description="")
    async def leave(self, ctx):
        state = self.get_state(ctx)

        if state.is_playing:
            state.player.stop()
            state.current = None

        if state.voice_client is not None:
            await state.voice_client.disconnect()
            state.voice_client = None

    @command(slug="play",
             templates=[
                 r"play (?P<url>.*)",
             ],
             short_description="Play a song or stream by the URL",
             long_description="")
    async def play(self, ctx, url):
        await ctx.bot.send_message(ctx.message.channel, "`play` command received")
        if url is not None:
            await ctx.bot.send_message(ctx.message.channel, f"parameter `url`={url}")

        state = self.get_state(ctx)

        if state.voice_client is None:
            await ctx.invoke(self.join)
            if state.voice_client is None:
                return

        state.add_entry(Entry(
            url,
            await state.voice_client.create_ytdl_player(
                url,
                use_avconv=True,
                ytdl_options=self.ytdl_options,
                after=state.next_entry
            )
        ))
        state.next_entry()

    @command(slug="resume",
             templates=[
                 r"resume",
                 r"play",
             ],
             short_description="Resume the currently playing song or stream",
             long_description="")
    async def resume(self, ctx):
        await ctx.bot.send_message(ctx.message.channel, "`resume` command received")

    @command(slug="pause",
             templates=[
                 r"pause",
             ],
             short_description="Pause the currently playing song or stream",
             long_description="")
    async def pause(self, ctx):
        await ctx.bot.send_message(ctx.message.channel, "`pause` command received")

    @command(slug="stop",
             templates=[
                 r"stop",
             ],
             short_description="Stop playing and reset current playlist state",
             long_description="")
    async def stop(self, ctx):
        await ctx.bot.send_message(ctx.message.channel, "`stop` command received")

    @command(slug="skip",
             templates=[
                 r"skip",
             ],
             short_description="Skip the currently playing song or stream",
             long_description="")
    async def skip(self, ctx):
        state = self.get_state(ctx)
        if state is None:
            await ctx.bot.send_message(ctx.message.channel, "Nothing is playing.")
            return

        if state.current is None:
            await ctx.bot.send_message(ctx.message.channel, "Playlist is stopped.")
            return

        state.player.stop()
        state.next_entry()

    @command(slug="playlist",
             templates=[
                 r"playlist",
             ],
             short_description="Show current playlist",
             long_description="")
    async def playlist(self, ctx):
        await ctx.bot.send_message(ctx.message.channel, "`playlist` command received")

    @command(slug="enqueue",
             templates=[
                 r"enqueue (?P<url>.*)"
             ],
             short_description="Add a song or stream to the current playlist",
             long_description="")
    async def enqueue(self, ctx, url):
        await ctx.bot.send_message(ctx.message.channel, "`enqueue` command received")
        if url is not None:
            await ctx.bot.send_message(ctx.message.channel, f"parameter `url`={url}")

    @command(slug="dequeue",
             templates=[
                r"dequeue (?P<url>.*)",
                r"dequeue",
             ],
             short_description="Remove a song or stream from the current playlist",
             long_description="")
    async def dequeue(self, ctx, url=None):
        await ctx.bot.send_message(ctx.message.channel, "`dequeue` command received")
        if url is not None:
            await ctx.bot.send_message(ctx.message.channel, f"parameter `url`={url}")

    @command(slug="shuffle",
             templates=[
                 r"shuffle",
             ],
             short_description="Shuffle songs and streams in the current playlist",
             long_description="")
    async def shuffle(self, ctx):
        await ctx.bot.send_message(ctx.message.channel, "`shuffle` command received")
