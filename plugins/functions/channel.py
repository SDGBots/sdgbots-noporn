# SCP-079-NOPORN - Auto delete NSFW media messages
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-NOPORN.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from time import sleep
from typing import List, Optional, Union

from pyrogram import Chat, Client, Message
from pyrogram.errors import FloodWait

from .. import glovar
from .etc import code, general_link, format_data, thread, user_mention
from .group import get_debug_text
from .telegram import send_message


# Enable logging
logger = logging.getLogger(__name__)


def ask_for_help(client: Client, level: str, gid: int, uid: int) -> bool:
    try:
        share_data(
            client=client,
            sender="NOPORN",
            receivers=["USER"],
            action="help",
            action_type=level,
            data={
                "group_id": gid,
                "user_id": uid
            }
        )
        return True
    except Exception as e:
        logger.warning(f"Ask for help error: {e}", exc_info=True)

    return False


def declare_message(client: Client, level: str, gid: int, mid: int) -> bool:
    try:
        share_data(
            client=client,
            sender="NOPORN",
            receivers=["LANG", "NOFLOOD", "NOSPAM", "USER"],
            action="declare",
            action_type=level,
            data={
                "group_id": gid,
                "message_id": mid
            }
        )
        return True
    except Exception as e:
        logger.warning(f"Declare message error: {e}", exc_info=True)

    return False


def forward_evidence(client: Client, message: Message, level: str, reason: str) -> Optional[Union[bool, int]]:
    result = None
    try:
        uid = message.from_user.id
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = message.forward(glovar.logging_channel_id)
            except FloodWait as e:
                flood_wait = True
                sleep(e.x + 1)
            except Exception as e:
                logger.info(f"Forward evidence message error: {e}", exc_info=True)
                return False

        result = result.message_id
        text = (f"项目编号：{general_link(glovar.project_name, glovar.project_link)}\n"
                f"用户 ID：{code(uid)}\n"
                f"操作等级：{code((lambda x: '自动封禁' if x == 'ban' else '自动删除')(level))}\n"
                f"规则：{code(reason)}")
        thread(send_message, (client, glovar.logging_channel_id, text, result))
    except Exception as e:
        logger.warning(f"Forward evidence error: {e}", exc_info=True)

    return result


def send_debug(client: Client, chat: Chat, action: str, uid: int, mid: int, eid: int) -> bool:
    text = get_debug_text(client, chat)
    text += (f"用户 ID：{user_mention(uid)}\n"
             f"执行操作：{code(action)}\n"
             f"触发消息："
             f"{general_link(mid, f'https://t.me/{glovar.logging_channel_username}/{eid}')}")
    thread(send_message, (client, glovar.debug_channel_id, text))

    return False


def share_bad_user(client: Client, uid: int) -> bool:
    try:
        share_data(
            client=client,
            sender="NOPORN",
            receivers=["LANG", "NOFLOOD", "NOSPAM", "USER", "WATCH"],
            action="add",
            action_type="bad",
            data={
                "id": uid,
                "type": "user"
            }
        )
        return True
    except Exception as e:
        logger.warning(f"Share bad user error: {e}", exc_info=True)

    return False


def share_data(client: Client, sender: str, receivers: List[str], action: str, action_type: str, data=None) -> bool:
    try:
        text = format_data(
            sender=sender,
            receivers=receivers,
            action=action,
            action_type=action_type,
            data=data
        )
        thread(send_message, (client, glovar.exchange_channel_id, text))
        return True
    except Exception as e:
        logger.warning(f"Share data error: {e}", exc_info=True)

    return False


def share_watch_ban_user(client: Client, uid: int) -> bool:
    try:
        share_data(
            client=client,
            sender="NOPORN",
            receivers=["LANG", "NOFLOOD", "NOSPAM"],
            action="add",
            action_type="watch",
            data={
                "id": uid,
                "type": "ban"
            }
        )
        return True
    except Exception as e:
        logger.warning(f"Share watch ban user error: {e}", exc_info=True)
