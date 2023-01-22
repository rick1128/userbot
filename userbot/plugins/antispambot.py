#    Copyright (C) 2020  sandeep.n(π.$)
# baning spmmers plugin for catuserbot by @sandy1709
# included both cas(combot antispam service) and spamwatch (need to add more feaututres)

from requests import get
from telethon.errors import ChatAdminRequiredError
from telethon.events import ChatAction
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.utils import get_display_name

from ..Config import Config
from ..sql_helper.gban_sql_helper import get_gbanuser, is_gbanned
from ..utils import is_admin
from . import BOTLOG, BOTLOG_CHATID, catub, edit_or_reply, logging, spamwatch

LOGS = logging.getLogger(__name__)
plugin_category = "admin"
if Config.ANTISPAMBOT_BAN:

    @catub.on(ChatAction())
    async def anti_spambot(event):  # sourcery no-metrics
        # sourcery skip: low-code-quality, use-fstring-for-formatting
        if not event.user_joined and not event.user_added:
            return
        user = await event.get_user()
        catadmin = await is_admin(event.client, event.chat_id, event.client.uid)
        if not catadmin:
            return
        catbanned = None
        adder = None
        ignore = None
        if event.user_added:
            try:
                adder = event.action_message.sender_id
            except AttributeError:
                return
        async for admin in event.client.iter_participants(
            event.chat_id, filter=ChannelParticipantsAdmins
        ):
            if admin.id == adder:
                ignore = True
                break
        if ignore:
            return
        if is_gbanned(user.id):
            catgban = get_gbanuser(user.id)
            if catgban.reason:
                hmm = await event.reply(
                    f"[{user.first_name}](tg://user?id={user.id}) was gbanned by you for the reason `{catgban.reason}`"
                )
            else:
                hmm = await event.reply(
                    f"[{user.first_name}](tg://user?id={user.id}) was gbanned by you"
                )
            try:
                await event.client.edit_permissions(
                    event.chat_id, user.id, view_messages=False
                )
                catbanned = True
            except Exception as e:
                LOGS.info(e)
        if spamwatch and not catbanned:
            if ban := spamwatch.get_ban(user.id):
                hmm = await event.reply(
                    f"[{user.first_name}](tg://user?id={user.id}) was banned by spamwatch for the reason `{ban.reason}`"
                )
                try:
                    await event.client.edit_permissions(
                        event.chat_id, user.id, view_messages=False
                    )
                    catbanned = True
                except Exception as e:
                    LOGS.info(e)
        if not catbanned:
            try:
                casurl = f"https://api.cas.chat/check?user_id={user.id}"
                data = get(casurl).json()
            except Exception as e:
                LOGS.info(e)
                data = None
            if data and data["ok"]:
                reason = (
                    f"[Banned by Combot Anti Spam](https://cas.chat/query?u={user.id})"
                )
                hmm = await event.reply(
                    f"[{user.first_name}](tg://user?id={user.id}) was banned by Combat anti-spam service(CAS) for the reason check {reason}"
                )
                try:
                    await event.client.edit_permissions(
                        event.chat_id, user.id, view_messages=False
                    )
                    catbanned = True
                except Exception as e:
                    LOGS.info(e)
        if BOTLOG and catbanned:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#ANTISPAMBOT\n"
                f"**المستخدم :** [{user.first_name}](tg://user?id={user.id})\n"
                f"**الكروب :** {get_display_name(await event.get_chat())} (`{event.chat_id}`)\n"
                f"**سبب :** {hmm.text}",
            )


@catub.cat_cmd(
    pattern="كاسك$",
    command=("cascheck", plugin_category),
    info={
        "header": "To check the users who are banned in cas",
        "description": "When you use this cmd it will check every user in the group where you used whether \
        he is banned in cas (combat antispam service) and will show there names if they are flagged in cas",
        "usage": "{tr}cascheck",
    },
    groups_only=True,
)
async def caschecker(event):
    "عمليات البحث عن cas(combot antispam service) المستخدمين المحظورين في المجموعة ويظهر لك القائمة"
    catevent = await edit_or_reply(
        event,
        "`التحقق من أي حالة(combot antispam service) المستخدمين المحظورين هنا ، قد يستغرق هذا عدة دقائق أيضًا......`",
    )
    text = ""
    try:
        info = await event.client.get_entity(event.chat_id)
    except (TypeError, ValueError) as err:
        return await event.edit(str(err))
    try:
        cas_count, members_count = (0,) * 2
        banned_users = ""
        async for user in event.client.iter_participants(info.id):
            if banchecker(user.id):
                cas_count += 1
                banned_users += (
                    f"حساب محذوف `{user.id}`\n"
                    if user.deleted
                    else f"{user.first_name}-`{user.id}`\n"
                )
            members_count += 1
        text = f"**تحذير!** وجد `{cas_count}` من `{members_count}` المستخدمون محظور عليهم كاس:\n"
        text += banned_users
        if not cas_count:
            text = "No CAS Banned users found!"
    except ChatAdminRequiredError as carerr:
        await catevent.edit("`كاسك فشل: امتيازات المسؤول مطلوبة`")
        return
    except BaseException as be:
        await catevent.edit("`فشل فحص كاس`")
        return
    await catevent.edit(text)


@catub.cat_cmd(
    pattern="فحص البريد العشوائي$",
    command=("spamcheck", plugin_category),
    info={
        "header": "To check the users who are banned in spamwatch",
        "description": "When you use this command it will check every user in the group where you used whether \
        he is banned in spamwatch federation and will show there names if they are banned in spamwatch federation",
        "usage": "{tr}spamcheck",
    },
    groups_only=True,
)
async def caschecker(event):
    "عمليات البحث عن اتحاد الساعات العشوائية حظرت المستخدمين في المجموعة ويظهر لك القائمة ♥️🧸"
    text = ""
    catevent = await edit_or_reply(
        event,
        "`التحقق من أي مستخدمين محظورين هنا ، قد يستغرق هذا عدة دقائق أيضًا 📍🧸......`",
    )
    try:
        info = await event.client.get_entity(event.chat_id)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return
    try:
        cas_count, members_count = (0,) * 2
        banned_users = ""
        async for user in event.client.iter_participants(info.id):
            if spamchecker(user.id):
                cas_count += 1
                banned_users += (
                    f"Deleted Account `{user.id}`\n"
                    if user.deleted
                    else f"{user.first_name}-`{user.id}`\n"
                )

            members_count += 1
        text = f"**تحذير! **وجد `{cas_count}` من `{members_count}` المستخدمون محظورون مشاهدة الرسائل غير المرغوب فيها ♥️🧸:\n"
        text += banned_users
        if not cas_count:
            text = "لم يتم العثور على مستخدمين محظورين!"
    except ChatAdminRequiredError as carerr:
        await catevent.edit("`فشل فحص ساعة البريد العشوائي: امتيازات المسؤول مطلوبة`")
        return
    except BaseException as be:
        await catevent.edit("`فشل التحقق من ساعة البريد العشوائي ♥️🧸`")
        return
    await catevent.edit(text)


def banchecker(user_id):
    try:
        casurl = f"https://api.cas.chat/check?user_id={user.id}"
        data = get(casurl).json()
    except Exception as e:
        LOGS.info(e)
        data = None
    return bool(data and data["ok"])


def spamchecker(user_id):
    ban = spamwatch.get_ban(user_id) if spamwatch else None
    return bool(ban)
