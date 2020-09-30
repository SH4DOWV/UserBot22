import asyncio
import random
import re
import time

from cowpy import cow

from userbot import CMD_HELP, ZALG_LIST
from userbot.events import register, grp_exclude

PORCONI = [
"porcodio",
"dio porcone",
"Madonna puttana",
"Gesù col culo magnetico nella valle dei cazzi di ferro",
"Madonna troia",
"Quei porconi dei Santi",
"Madonna puttanona",
"Madonna inculata dagli Apostoli",
"Grazie Giuda per averlo ucciso",
"Oggi mangio Gesù, arrostito sul fuoco è buono",
"Dio transenna",
"Gesù martellato",
]

@register(outgoing=True, pattern="^.pd$")
@grp_exclude()
async def react_meme(react):
    """ Make your userbot react to everything. """
    if not react.text[0].isalpha() and react.text[0] not in ("/", "#", "@",
                                                             "!"):
        index = random.randint(0, len(PORCONI))
        reply_text = PORCONI[index]
        await react.edit(reply_text)


