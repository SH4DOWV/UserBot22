# Copyright (C) 2020 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Paperplane module for kanging stickers or making new ones. """

import io
import math
import urllib.request
from PIL import Image

from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto, InputPeerNotifySettings
from telethon.tl.functions.account import UpdateNotifySettingsRequest

from userbot import CMD_HELP, bot
from userbot.events import register, grp_exclude

PACK_FULL = "Whoa! That's probably enough stickers for one pack, give it a break. \
A pack can't have more than 120 stickers at the moment."
PACK_DOESNT_EXIST = "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>."


@register(outgoing=True, pattern="^.kang($| )?((?![0-9]).+?)? ?([0-9]*)?")
@grp_exclude()
async def kang(event):
    """ Function for .kang command, create a sticker pack and add stickers. """
    await event.edit('`Fottendoti lo Sticker...`')
    user = await bot.get_me()
    pack_username = ''
    if not user.username:
        try:
            user.first_name.decode('ascii')
            pack_username = user.first_name
        except UnicodeDecodeError: # User's first name isn't ASCII, use ID instead
            pack_username = user.id
    else: pack_username = user.username

    textx = await event.get_reply_message()
    emoji = event.pattern_match.group(2)
    number = int(event.pattern_match.group(3) or 1) # If no number specified, use 1
    new_pack = False

    if textx.photo or textx.sticker: message = textx
    elif event.photo or event.sticker: message = event
    else:
        await event.edit("`Hai bisogno di mandare una giusta foto/sticker per prenderla!`")
        return

    sticker = io.BytesIO()
    await bot.download_media(message, sticker)
    sticker.seek(0)

    if not sticker:
        await event.edit("`Non ho pouto caricare lo sticker! Vedi se hai mandato uno sticker/foto giusto.`")
        return

    is_anim = message.file.mime_type == "application/x-tgsticker"
    if not is_anim:
        img = await resize_photo(sticker)
        sticker.name = "sticker.png"
        sticker.seek(0)
        img.save(sticker, "PNG")

    # The user didn't specify an emoji...
    if not emoji:
        if message.file.emoji: # ...but the sticker has one
            emoji = message.file.emoji
        else: # ...and the sticker doesn't have one either
            emoji = "🤔"

    packname = f"a{user.id}_da_{pack_username}_{number}{'_anim' if is_anim else ''}"
    packtitle = (f"@{user.username or user.first_name} bel Pack "
                f"{number}{' animated' if is_anim else ''}")
    response = urllib.request.urlopen(
            urllib.request.Request(f'http://t.me/addstickers/{packname}'))
    htmlstr = response.read().decode("utf8").split('\n')
    new_pack = PACK_DOESNT_EXIST in htmlstr

    # Mute Stickers bot to ensure user doesn't get notification spam
    muted = await bot(UpdateNotifySettingsRequest(
        peer='t.me/Stickers',
        settings=InputPeerNotifySettings(mute_until=2**31-1)) # Mute forever
    )
    if not muted: # Tell the user just in case, this may rarely happen
        await event.edit(
            "`L'userbot non può mutare lo Sticker bot.`")

    if new_pack:
        await event.edit("`Questo Pack non esiste! Creando un nuovo Pack...`")
        await newpack(is_anim, sticker, emoji, packtitle, packname)
    else:
        async with bot.conversation('t.me/Stickers') as conv:
            # Cancel any pending command
            await conv.send_message('/cancel')
            await conv.get_response()

            # Send the add sticker command
            await conv.send_message('/addsticker')
            await conv.get_response()

            # Send the pack name
            await conv.send_message(packname)
            x = await conv.get_response()

            # Check if the selected pack is full
            while x.text == PACK_FULL:
                # Switch to a new pack, create one if it doesn't exist
                number += 1
                packname = f"a{user.id}_da_{pack_username}_{number}{'_anim' if is_anim else ''}"
                packtitle = (f"@{user.username or user.first_name} bel Pack "
                            f"{number}{' animated' if is_anim else ''}")

                await event.edit(
                    f"`Cambiano al Pack {number} per spazio insufficiente nel Pack {number-1}.`"
                )

                await conv.send_message(packname)
                x = await conv.get_response()
                if x.text == "Pack selezionato non valido.": # That pack doesn't exist
                    await newpack(is_anim, sticker, emoji, packtitle, packname)

                    # Read all unread messages
                    await bot.send_read_acknowledge('t.me/Stickers')
                    # Unmute Stickers bot back
                    muted = await bot(UpdateNotifySettingsRequest(
                        peer='t.me/Stickers',
                        settings=InputPeerNotifySettings(mute_until=None))
                    )

                    await event.edit(
                        f"`Sticker aggiunto al Pack {number}{'(animated)' if is_anim else ''} con "
                        f"{emoji} come emote! "
                        f"Questo Pack può essere trovato `[qui](t.me/addstickers/{packname})",
                        parse_mode='md')
                    return

            # Upload the sticker file
            if is_anim:
                upload = await message.client.upload_file(sticker, file_name="AnimatedSticker.tgs")
                await conv.send_file(upload, force_document=True)
            else:
                sticker.seek(0)
                await conv.send_file(sticker, force_document=True)
            await conv.get_response()

            # Send the emoji
            await conv.send_message(emoji)
            await conv.get_response()

            # Finish editing the pack
            await conv.send_message('/done')
            await conv.get_response()

    # Read all unread messages
    await bot.send_read_acknowledge('t.me/Stickers')
    # Unmute Stickers bot back
    muted = await bot(UpdateNotifySettingsRequest(
        peer='t.me/Stickers',
        settings=InputPeerNotifySettings(mute_until=None))
    )

    await event.edit(
        f"`Sticker aggiunto al Pack {number}{'(animated)' if is_anim else ''} con "
        f"{emoji} come emote! "
        f"Questo può essere trovato `[qui](t.me/addstickers/{packname})",
        parse_mode='md')


async def newpack(is_anim, sticker, emoji, packtitle, packname):
    async with bot.conversation('Stickers') as conv:
        # Cancel any pending command
        await conv.send_message('/cancel')
        await conv.get_response()

        # Send new pack command
        if is_anim:
            await conv.send_message('/newanimated')
        else:
            await conv.send_message('/newpack')
        await conv.get_response()

        # Give the pack a name
        await conv.send_message(packtitle)
        await conv.get_response()

        # Upload sticker file
        if is_anim:
            upload = await bot.upload_file(sticker, file_name="AnimatedSticker.tgs")
            await conv.send_file(upload, force_document=True)
        else:
            sticker.seek(0)
            await conv.send_file(sticker, force_document=True)
        await conv.get_response()

        # Send the emoji
        await conv.send_message(emoji)
        await conv.get_response()

        # Publish the pack
        await conv.send_message("/publish")
        if is_anim:
            await conv.get_response()
            await conv.send_message(f"<{packtitle}>")
        await conv.get_response()

        # Skip pack icon selection
        await conv.send_message("/skip")
        await conv.get_response()

        # Send packname
        await conv.send_message(packname)
        await conv.get_response()

async def resize_photo(photo):
    """ Resize the given photo to 512x512 """
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)

    return image


CMD_HELP.update({
    "kang": [
        "Kang",
        " - `.kang <emoji> <number>`: Reply .kang to a sticker or an image to kang "
        "it to your Paperplane pack.\n"
        "If emojis are sent, they will be used as the emojis for the sticker.\n"
        "If a number is sent, the emoji will be saved in the pack corresponding to that number."
    ]
})
