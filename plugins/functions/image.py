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

from PIL import Image
from pyrogram import Message
from nsfw import classify

from .. import glovar

# Enable logging
logger = logging.getLogger(__name__)


def get_file_id(message: Message) -> str:
    # Get media message's file id
    if (message.photo or message.sticker or (message.animation and message.animation.thumb)
            or (message.video and message.video.thumb)
            or (message.video_note and message.video_note.thumb)
            or (message.document and message.document.thumb)
            or (message.audio and message.audio.thumb)):
        if message.photo:
            file_id = message.photo.sizes[-1].file_id
        elif message.sticker:
            file_id = message.sticker.file_id
        elif message.animation:
            file_id = message.animation.thumb.file_id
        elif message.video:
            file_id = message.video.thumb.file_id
        elif message.video_note:
            file_id = message.video_note.thumb.file_id
        elif message.document:
            if (message.document.mime_type
                    and "image" in message.document.mime_type
                    and "gif" not in message.document.mime_type
                    and message.document.file_size
                    and message.document.file_size < glovar.image_size):
                file_id = message.document.file_id
            else:
                file_id = message.document.thumb.file_id
        else:
            file_id = message.audio.thumb.file_id
    else:
        file_id = ""

    return file_id


def get_porn(path: str) -> float:
    # Get porn score
    porn = 0
    try:
        image = Image.open(path)
        sfw, nsfw = classify(image)
        porn = nsfw
    except Exception as e:
        logger.warning(f"Get porn error: {e}", exc_info=True)

    return porn
