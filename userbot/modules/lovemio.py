import asyncio
import random
import re
import time

from cowpy import cow

from userbot import CMD_HELP, ZALG_LIST
from userbot.events import register, grp_exclude

EMOJIS = [
"❤️",
"💖",
"💞",
"💕",
"❣",
]

@register(outgoing=True, pattern="^.love(?: |$)(.*)")
@grp_exclude()
async def claptext(memereview):
    """ Praise people! """
    if not memereview.text[0].isalpha() and memereview.text[0] not in (
            "/", "#", "@", "!"):
        textx = await memereview.get_reply_message()
        message = memereview.pattern_match.group(1)
        rmc = random.choice(EMOJIS)
        if message:
            pass
        elif textx:
            message = textx.text
        else:
            await memereview.edit("**Io non amo le persone inutilmente!**")
            return
        reply_text = random.choice(EMOJIS)
        reply_text += message.replace(" ", (random.choice(EMOJIS)))
        reply_text += random.choice(EMOJIS)
        await memereview.edit(reply_text)