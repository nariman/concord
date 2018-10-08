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

import enum


class EventType(enum.Enum):
    """List of event types which can be received."""

    UNKNOWN = None

    CONNECT = "connect"
    ERROR = "error"
    GROUP_JOIN = "group_join"
    GROUP_REMOVE = "group_remove"
    GUILD_AVAILABLE = "guild_available"
    GUILD_CHANNEL_CREATE = "guild_channel_create"
    GUILD_CHANNEL_DELETE = "guild_channel_delete"
    GUILD_CHANNEL_PINS_UPDATE = "guild_channel_pins_update"
    GUILD_CHANNEL_UPDATE = "guild_channel_update"
    GUILD_EMOJIS_UPDATE = "guild_emojis_update"
    GUILD_JOIN = "guild_join"
    GUILD_REMOVE = "guild_remove"
    GUILD_ROLE_CREATE = "guild_role_create"
    GUILD_ROLE_DELETE = "guild_role_delete"
    GUILD_ROLE_UPDATE = "guild_role_update"
    GUILD_UNAVAILABLE = "guild_unavailable"
    GUILD_UPDATE = "guild_update"
    MEMBER_BAN = "member_ban"
    MEMBER_JOIN = "member_join"
    MEMBER_REMOVE = "member_remove"
    MEMBER_UNBAN = "member_unban"
    MEMBER_UPDATE = "member_update"
    MESSAGE = "message"
    MESSAGE_DELETE = "message_delete"
    MESSAGE_EDIT = "message_edit"
    PRIVATE_CHANNEL_CREATE = "private_channel_create"
    PRIVATE_CHANNEL_DELETE = "private_channel_delete"
    PRIVATE_CHANNEL_PINS_UPDATE = "private_channel_pins_update"
    PRIVATE_CHANNEL_UPDATE = "private_channel_update"
    RAW_BULK_MESSAGE_DELETE = "raw_bulk_message_delete"
    RAW_MESSAGE_DELETE = "raw_message_delete"
    RAW_MESSAGE_EDIT = "raw_message_edit"
    RAW_REACTION_ADD = "raw_reaction_add"
    RAW_REACTION_CLEAR = "raw_reaction_clear"
    RAW_REACTION_REMOVE = "raw_reaction_remove"
    REACTION_ADD = "reaction_add"
    REACTION_CLEAR = "reaction_clear"
    REACTION_REMOVE = "reaction_remove"
    READY = "ready"
    RELATIONSHIP_ADD = "relationship_add"
    RELATIONSHIP_REMOVE = "relationship_remove"
    RELATIONSHIP_UPDATE = "relationship_update"
    RESUMED = "resumed"
    SHARD_READY = "shard_ready"
    SOCKET_RAW_RECEIVE = "socket_raw_receive"
    SOCKET_RAW_SEND = "socket_raw_send"
    SOCKET_RESPONSE = "socket_response"
    TYPING = "typing"
    VOICE_STATE_UPDATE = "voice_state_update"
    WEBHOOKS_UPDATE = "webhooks_update"
