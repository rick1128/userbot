import html

from userbot import catub
from userbot.core.logger import logging

from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper import warns_sql as sql

logger = logging.getLogger(__name__)

plugin_category = "admin"


@catub.cat_cmd(
    pattern="تحذير(?:\s|$)([\s\S]*)",
    command=("warn", plugin_category),
    info={
        "header": "لتحذير مستخدم.",
        "description": "ُسيحذر الشخص الذي راد عليه.",
        "usage": "{tr}warn <reason>",
    },
)
async def _(event):
    "To warn a user"
    warn_reason = event.pattern_match.group(1)
    if not warn_reason:
        warn_reason = "No reason"
    reply_message = await event.get_reply_message()
    limit, soft_warn = sql.get_warn_setting(event.chat_id)
    num_warns, reasons = sql.warn_user(
        reply_message.sender_id, event.chat_id, warn_reason
    )
    if num_warns >= limit:
        sql.reset_warns(reply_message.sender_id, event.chat_id)
        if soft_warn:
            logger.info("TODO: kick user")
            reply = f"{limit} التحذيرات, [user](tg://user?id={reply_message.sender_id}) تم طردة!"
        else:
            logger.info("TODO: ban user")
            reply = f"{limit} warnings, [user](tg://user?id={reply_message.sender_id}) تم حظرة!"
    else:
        reply = f"[user](tg://user?id={reply_message.sender_id}) لدية {num_warns}/{limit} تحذيرات... watch out!"
        if warn_reason:
            reply += f"\nسبب التحذير:\n{html.escape(warn_reason)}"
    await edit_or_reply(event, reply)


@catub.cat_cmd(
    pattern="تحذيراتة",
    command=("warns", plugin_category),
    info={
        "header": "لرؤية قائمة المحذرين.",
        "usage": "{tr}warns <reply>",
    },
)
async def _(event):
    "To get users warns list"
    reply_message = await event.get_reply_message()
    if not reply_message:
        return await edit_delete(event, "__قم بالرد على المستخدم لرؤية على تحذيراته.__")
    result = sql.get_warns(reply_message.sender_id, event.chat_id)
    if not result or result[0] == 0:
        return await edit_or_reply(event, "this user hasn't got any warnings!")
    num_warns, reasons = result
    limit, soft_warn = sql.get_warn_setting(event.chat_id)
    if not reasons:
        return await edit_or_reply(
            event,
            f"هذا المستخدم لدية {num_warns} / {limit} من التحذيرات, لكن لا توجد أسباب لأي منهم.",
        )
    text = f"هذا المستخدم لدية {num_warns}/{limit} من تحذيرات, لأسباب:"
    text += "\r\n"
    text += الاسباب
    await event.edit(text)


@catub.cat_cmd(
    pattern="م(سح)?التحذيرات$",
    command=("resetwarns", plugin_category),
    info={
        "header": "لمسح تحذيرات المستخدم",
        "usage": [
            "{tr}rwarns",
            "{tr}resetwarns",
        ],
    },
)
async def _(event):
    "To reset warns"
    reply_message = await event.get_reply_message()
    sql.reset_warns(reply_message.sender_id, event.chat_id)
    await edit_or_reply(event, "__تم مسح التحذيرات!__")
