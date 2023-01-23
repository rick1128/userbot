from telethon.utils import pack_bot_file_id

from userbot import catub
from userbot.core.logger import logging

from ..core.managers import edit_delete, edit_or_reply

plugin_category = "utils"

LOGS = logging.getLogger(__name__)


@catub.cat_cmd(
    pattern="(ايدي|الايدي)(?:\s|$)([\s\S]*)",
    command=("id", plugin_category),
    info={
        "header": "To get id of the group or user.",
        "description": "if given input then shows id of that given chat/channel/user else if you reply to user then shows id of the replied user \
    along with current chat id and if not replied to user or given input then just show id of the chat where you used the command",
        "usage": "{tr}id <reply/username>",
    },
)
async def _(event):
    "للحصول على ايدي المجموعة أو المستخدم."
    if input_str := event.pattern_match.group(2):
        try:
            p = await event.client.get_entity(input_str)
        except Exception as e:
            return await edit_delete(event, f"`{e}`", 5)
        try:
            if p.first_name:
                return await edit_or_reply(
                    event, f"ايدي المستخدم ♥️🧸 `{input_str}` هذا `{p.id}`"
                )
        except Exception:
            try:
                if p.title:
                    return await edit_or_reply(
                        event, f"ايدي الدردشة / القناة `{p.title}` هذا `{p.id}`"
                    )
            except Exception as e:
                LOGS.info(str(e))
        await edit_or_reply(event, "`إما أن تعطي مدخلات كاسم مستخدم أو ترد على المستخدم ♥️🧸`")
    elif event.reply_to_msg_id:
        r_msg = await event.get_reply_message()
        if r_msg.media:
            bot_api_file_id = pack_bot_file_id(r_msg.media)
            await edit_or_reply(
                event,
                f"**ايدي الدردشة الحالي : **`{event.chat_id}`\n**من ايدي المستخدم ♥️🧸: **`{r_msg.sender_id}`\n**ايدي ملف الوسائط: **`{bot_api_file_id}`",
            )

        else:
            await edit_or_reply(
                event,
                f"**ايدي الدردشة الحالي ♥️🧸 : **`{event.chat_id}`\n**من ايدي المستخدم ♥️🧸: **`{r_msg.sender_id}`",
            )

    else:
        await edit_or_reply(event, f"**ايدي الدردشة الحالي ♥️🧸 : **`{event.chat_id}`")
