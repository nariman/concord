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

import sys
from itertools import chain

import discord
import pendulum

from hugo.command import (
    Template,
    Command,
    Group
)


class Mention:
    def __init__(self, mention, is_short=False):
        self.mention = mention
        self.is_short = is_short

    def match(self, message: discord.Message):
        if message.content.startswith(self.mention):
            return True
        return False

    def __str__(self):
        return self.mention


class Bot(discord.Client, Group):
    def __init__(self, name, *, allow_short_mention=False, 
                 respond_to_bot_messages=False, loop=None, **options):
        discord.Client.__init__(self, loop=loop, **options)
        Group.__init__(self, name)

        self.initialized = False

        self.name = name
        self.allow_short_mention = allow_short_mention
        self.respond_to_bot_messages = respond_to_bot_messages

        self.bot_mentions = [Mention("/", is_short=True)]
        self.bot_mentions.extend(self.format_mentions_by_name(self.name))

        self.add_group = self.add_subgroup
        self.remove_group = self.remove_subgroup

    @staticmethod
    def format_mentions_by_name(name):
        return [
            Mention(f"{name} "), Mention(f"{name},")
        ]

    def detect_bot_mention(self, message: discord.Message):
        for mention in self.bot_mentions:
            if mention.is_short and not self.allow_short_mention:
                continue
            if mention.match(message):
                return mention
        return None

    async def on_ready(self):
        if not self.initialized:
            self.uptime = pendulum.utcnow()
            self.bot_mentions.extend(
                self.format_mentions_by_name(self.user.mention))

            self.initialized = True

    async def on_message(self, message: discord.Message):
        if message.author.bot and not self.respond_to_bot_messages:
            return

        mention = self.detect_bot_mention(message)
        if mention is None:
            return

        content = message.content[len(str(mention)):]

        for callback in self.flatten:
            if (message.channel.is_private 
                and not callback.command.private_messages):
                continue
            if (not message.channel.is_private 
                and not callback.command.server_messages):
                continue

            for template in callback.command.templates:
                if mention.is_short and not template.allow_short_mention:
                    continue
                match = template.compiled.match(content)

                if match:
                    await self.send_typing(message.channel)
                    ctx = Context(self, message, callback, mention, template, 
                                  match)

                    try:
                        await callback(ctx=ctx, **match.groupdict())
                    except:
                        await ctx.send_message("Error during processing your request")
                        await ctx.send_message(sys.exc_info()[0])
                    return


class Context:
    def __init__(self, bot: Bot, message: discord.Message, callback, 
                 mention: Mention, template: Template, match):
        self.bot = bot
        self.message = message
        self.callback = callback
        self.mention = mention
        self.template = template
        self.match = match

    @property
    def command(self):
        return self.callback.command

    @property
    def author(self):
        return self.message.author

    @property
    def server(self):
        return self.message.server

    @property
    def channel(self):
        return self.message.channel

    async def send_message(self, *args, **kwargs):
        return await self.bot.send_message(self.message.channel, *args, 
                                           **kwargs)
