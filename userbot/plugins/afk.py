import asyncio
from datetime import datetime

from telethon.tl import functions, types

from userbot import catub

from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.tools import media_type
from ..helpers.utils import _format
from . import BOTLOG, BOTLOG_CHATID

plugin_category = "utils"

LOGS = logging.getLogger(__name__)


class AFK:
    def __init__(self):
        self.USERAFK_ON = {}
        self.afk_time = None
        self.last_afk_message = {}
        self.afk_star = {}
        self.afk_end = {}
        self.reason = None
        self.msg_link = False
        self.afk_type = None
        self.media_afk = None
        self.afk_on = False


AFK_ = AFK()


@catub.cat_cmd(outgoing=True, edited=False)
async def set_not_afk(event):
    if AFK_.afk_on is False:
        return
    back_alive = datetime.now()
    AFK_.afk_end = back_alive.replace(microsecond=0)
    if AFK_.afk_star != {}:
        total_afk_time = AFK_.afk_end - AFK_.afk_star
        time = int(total_afk_time.seconds)
        d = time // (24 * 3600)
        time %= 24 * 3600
        h = time // 3600
        time %= 3600
        m = time // 60
        time %= 60
        s = time
        endtime = ""
        if d > 0:
            endtime += f"{d}d {h}h {m}m {s}s"
        elif h > 0:
            endtime += f"{h}h {m}m {s}s"
        else:
            endtime += f"{m}m {s}s" if m > 0 else f"{s}s"
    current_message = event.message.message
    if (("afk" not in current_message) or ("#afk" not in current_message)) and (
        "on" in AFK_.USERAFK_ON
    ):
        shite = await event.client.send_message(
            event.chat_id,
            "`لقد عدت من.\nWas السليب 😴 " + endtime + "`",
        )
        AFK_.USERAFK_ON = {}
        AFK_.afk_time = None
        await asyncio.sleep(5)
        await shite.delete()
        AFK_.afk_on = False
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#AFKFALSE \n`Set AFK mode to False\n"
                + "لقد عدت من.\nالسليب 😴 "
                + endtime
                + "`",
            )


@catub.cat_cmd(
    incoming=True, func=lambda e: bool(e.mentioned or e.is_private), edited=False
)
async def on_afk(event):  # sourcery no-metrics
    # sourcery skip: low-code-quality
    if AFK_.afk_on is False:
        return
    back_alivee = datetime.now()
    AFK_.afk_end = back_alivee.replace(microsecond=0)
    if AFK_.afk_star != {}:
        total_afk_time = AFK_.afk_end - AFK_.afk_star
        time = int(total_afk_time.seconds)
        d = time // (24 * 3600)
        time %= 24 * 3600
        h = time // 3600
        time %= 3600
        m = time // 60
        time %= 60
        s = time
        endtime = ""
        if d > 0:
            endtime += f"{d}d {h}h {m}m {s}s"
        elif h > 0:
            endtime += f"{h}h {m}m {s}s"
        else:
            endtime += f"{m}m {s}s" if m > 0 else f"{s}s"
    current_message_text = event.message.message.lower()
    if "afk" in current_message_text or "#afk" in current_message_text:
        return False
    if not await event.get_sender():
        return
    if AFK_.USERAFK_ON and not (await event.get_sender()).bot:
        msg = None
        if AFK_.afk_type == "media":
            if AFK_.reason:
                message_to_reply = (
                    f"`أنا نائم او مشغول  .\n\nمنذ {endtime}\nالسبب : {AFK_.reason}`"
                )
            else:
                message_to_reply = f"`انا نائم او مشغول .\n\nمنذ {endtime}\nالسبب : غير مذكور ( ಠ ʖ̯ ಠ)`"
            if event.chat_id:
                msg = await event.reply(message_to_reply, file=AFK_.media_afk.media)
        elif AFK_.afk_type == "text":
            if AFK_.msg_link and AFK_.reason:
                message_to_reply = (
                    f"**أنا نائم او مشغول .\n\nمنذ {endtime}\nالسبب : **{AFK_.reason}"
                )
            elif AFK_.reason:
                message_to_reply = (
                    f"`أنا نائم او مشغول .\n\nمنذ {endtime}\nالسبب : {AFK_.reason}`"
                )
            else:
                message_to_reply = f"`انا نائم او مشغول .\n\nAFK Since {endtime}\nالسبب : غير مذكور ( ಠ ʖ̯ ಠ)`"
            if event.chat_id:
                msg = await event.reply(message_to_reply)
        if event.chat_id in AFK_.last_afk_message:
            await AFK_.last_afk_message[event.chat_id].delete()
        AFK_.last_afk_message[event.chat_id] = msg
        if event.is_private:
            return
        hmm = await event.get_chat()
        if Config.PM_LOGGER_GROUP_ID == -100:
            return
        full = None
        try:
            full = await event.client.get_entity(event.message.from_id)
        except Exception as e:
            LOGS.info(str(e))
        messaget = await media_type(event)
        resalt = f"#AFK_TAGS \n<b>كروب : </b><code>{hmm.title}</code>"
        if full is not None:
            resalt += f"\n<b>من : </b> 👤{_format.htmlmentionuser(full.first_name , full.id)}"
        if messaget is not None:
            resalt += f"\n<b>نوع الرسالة : </b><code>{messaget}</code>"
        else:
            resalt += f"\n<b>الرسالة : </b>{event.message.message}"
        resalt += f"\n<b>رابط الرسالة: </b><a href = 'https://t.me/c/{hmm.id}/{event.message.id}'> link</a>"
        if not event.is_private:
            await event.client.send_message(
                Config.PM_LOGGER_GROUP_ID,
                resalt,
                parse_mode="html",
                link_preview=False,
            )


@catub.cat_cmd(
    pattern="سليب(?:\s|$)([\s\S]*)",
    command=("afk", plugin_category),
    info={
        "header": "Enables afk for your account",
        "description": "When you are in afk if any one tags you then your bot will reply as he is offline.\
        AFK mean away from keyboard.",
        "options": "If you want AFK reason with hyperlink use [ ; ] after reason, then paste the media link.",
        "usage": [
            "{tr}afk <reason>",
            "{tr}afk <reason> ; <link>",
        ],
        "examples": "{tr}afk Let Me Sleep",
        "note": "Switches off AFK when you type back anything, anywhere. You can use #afk in message to continue in afk without breaking it",
    },
)
async def _(event):
    "لوضع علامة على نفسك على أنك سليب ، أي بعيدا عن لوحة المفاتيح"
    AFK_.USERAFK_ON = {}
    AFK_.afk_time = None
    AFK_.last_afk_message = {}
    AFK_.afk_end = {}
    AFK_.afk_type = "text"
    start_1 = datetime.now()
    AFK_.afk_on = True
    AFK_.afk_star = start_1.replace(microsecond=0)
    if not AFK_.USERAFK_ON:
        input_str = event.pattern_match.group(1)
        if ";" in input_str:
            msg, mlink = input_str.split(";", 1)
            AFK_.reason = f"[{msg.strip()}]({mlink.strip()})"
            AFK_.msg_link = True
        else:
            AFK_.reason = input_str
            AFK_.msg_link = False
        last_seen_status = await event.client(
            functions.account.GetPrivacyRequest(types.InputPrivacyKeyStatusTimestamp())
        )
        if isinstance(last_seen_status.rules, types.PrivacyValueAllowAll):
            AFK_.afk_time = datetime.now()
        AFK_.USERAFK_ON = f"on: {AFK_.reason}"
        if AFK_.reason:
            await edit_delete(
                event, f"`I shall be Going afk! because ~` {AFK_.reason}", 5
            )
        else:
            await edit_delete(event, "`I shall be Going afk! `", 5)
        if BOTLOG:
            if AFK_.reason:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    f"#AFKTRUE \nSet AFK mode to True, and Reason is {AFK_.reason}",
                )
            else:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "#AFKTRUE \nSet AFK mode to True, and Reason is Not Mentioned",
                )


@catub.cat_cmd(
    pattern="mafk(?:\s|$)([\s\S]*)",
    command=("mafk", plugin_category),
    info={
        "header": "Enables afk for your account",
        "description": "When you are in afk if any one tags you then your bot will reply as he is offline.\
         AFK mean away from keyboard. Here it supports media unlike afk command",
        "options": "If you want AFK reason with hyperlink use [ ; ] after reason, then paste the media link.",
        "usage": [
            "{tr}mafk <reason> and reply to media",
        ],
        "examples": "{tr}mafk Let Me Sleep",
        "note": "Switches off AFK when you type back anything, anywhere. You can use #afk in message to continue in afk without breaking it",
    },
)
async def _(event):
    "To mark yourself as afk i.e. Away from keyboard (supports media)"
    reply = await event.get_reply_message()
    media_t = await media_type(reply)
    if media_t == "Sticker" or not media_t:
        return await edit_or_reply(
            event, "`لم تقم بالرد على أي وسائط لتنشيط التركيز البؤري التلقائي للوسائط`"
        )
    if not BOTLOG:
        return await edit_or_reply(
            event, "`اذا كنت تريد وضع ميديا مع السليب فعليك وضع الفارات PRIVATE_GROUP_BOT_API_ID config`"
        )
    AFK_.USERAFK_ON = {}
    AFK_.afk_time = None
    AFK_.last_afk_message = {}
    AFK_.afk_end = {}
    AFK_.media_afk = None
    AFK_.afk_type = "media"
    start_1 = datetime.now()
    AFK_.afk_on = True
    AFK_.afk_star = start_1.replace(microsecond=0)
    if not AFK_.USERAFK_ON:
        input_str = event.pattern_match.group(1)
        AFK_.reason = input_str
        last_seen_status = await event.client(
            functions.account.GetPrivacyRequest(types.InputPrivacyKeyStatusTimestamp())
        )
        if isinstance(last_seen_status.rules, types.PrivacyValueAllowAll):
            AFK_.afk_time = datetime.now()
        AFK_.USERAFK_ON = f"on: {AFK_.reason}"
        if AFK_.reason:
            await edit_delete(
                event, f"سأكون ذاهبا للسليب! لأن` ~` {AFK_.reason}", 5
            )
        else:
            await edit_delete(event, "`سأكون ذاهبا للسليب!`", 5)
        AFK_.media_afk = await reply.forward_to(BOTLOG_CHATID)
        if AFK_.reason:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#AFKTRUE \nاضبط وضع السليب على صواب، والسبب هو {AFK_.reason}",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#AFKTRUE \nاضبط وضع السليب على صواب والسبب هو",
            )
