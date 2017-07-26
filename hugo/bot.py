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

from itertools import chain

import discord
import pendulum

from hugo.command import (
    Command,
    Group
)


class Bot(discord.Client, Group):
    def __init__(self, name, *, allow_slash_commands=False, loop=None, **options):
        discord.Client.__init__(self, loop=loop, **options)
        Group.__init__(self, name)

        self.name = name
        self.allow_slash_commands = allow_slash_commands

        self.add_group = self.add_subgroup
        self.remove_group = self.remove_subgroup

    def bot_mentions(self, message: discord.Message=None):
        """Returns all allowed bot mentions."""
        me = (self.user if message is None or message.server is None
              else message.server.me)
        return [
            f"{self.name} ", f"{self.name},",
            f"{me.mention} ", f"{me.mention},",
        ]

    def is_bot_mentioned(self, message: discord.Message):
        for mention in self.bot_mentions(message):
            if message.content.startswith(mention):
                return True
        return False

    def remove_bot_mention(self, content: str):
        for mention in self.bot_mentions():
            if content.startswith(mention):
                return content[len(mention):]
        return content

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.uptime = pendulum.utcnow()

    async def _proccess_message(self, message: discord.Message, 
                                is_slash: bool=False):
        content = message.content
        if is_slash:
            content = content[1:]
        else:
            content = self.remove_bot_mention(content)

        for callback in self.flatten:
            if (message.channel.is_private 
                and not callback.command.private_messages):
                continue
            if (not message.channel.is_private 
                and not callback.command.server_messages):
                continue

            raws = callback.command.slashes
            compiled = callback.command.compiled_slashes

            if not is_slash:
                raws = chain(raws, callback.command.templates)
                compiled = chain(compiled, callback.command.compiled_templates)

            for raw, compiled in zip(raws, compiled):
                match = compiled.match(content)

                if match:
                    await self.send_typing(message.channel)
                    ctx = Context(self, message, callback, match, 
                                  is_slash=is_slash)
                    await callback(ctx=ctx, **match.groupdict())
                    return

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.allow_slash_commands and message.content.startswith("/"):
            await self._proccess_message(message, is_slash=True)
        elif self.is_bot_mentioned(message):
            await self._proccess_message(message, is_slash=False)
        return


class Context:
    def __init__(self, bot: Bot, message: discord.Message, callback, match,
                 is_slash=False):
        self.bot = bot
        self.message = message
        self.callback = callback
        self.match = match
        self.is_slash = is_slash

    @property
    def command(self):
        return self.callback.command

    async def send_message(self, *args, **kwargs):
        return await self.bot.send_message(self.message.channel, *args, **kwargs)
