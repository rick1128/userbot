import os

from telethon.errors.rpcerrorlist import UsernameOccupiedError
from telethon.tl import functions
from telethon.tl.functions.account import UpdateUsernameRequest
from telethon.tl.functions.channels import GetAdminedPublicChannelsRequest
from telethon.tl.functions.photos import DeletePhotosRequest, GetUserPhotosRequest
from telethon.tl.types import Channel, Chat, InputPhoto, User

from userbot import catub

from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply

LOGS = logging.getLogger(__name__)
plugin_category = "utils"


# ====================== CONSTANT ===============================
INVALID_MEDIA = "```The extension of the media entity is invalid.```"
PP_CHANGED = "```Profile picture changed successfully.```"
PP_TOO_SMOL = "```This image is too small, use a bigger image.```"
PP_ERROR = "```Failure occured while processing image.```"
BIO_SUCCESS = "```Successfully edited Bio.```"
NAME_OK = "```Your name was successfully changed.```"
USERNAME_SUCCESS = "```Your username was successfully changed.```"
USERNAME_TAKEN = "```This username is already taken.```"
# ===============================================================


@catub.cat_cmd(
    pattern="وضع بايو ([\s\S]*)",
    command=("pbio", plugin_category),
    info={
        "header": "To set bio for this account.",
        "usage": "{tr}pbio <your bio>",
    },
)
async def _(event):
    "لتعيين السيرة الذاتية لهذا الحساب."
    bio = event.pattern_match.group(1)
    try:
        await event.client(functions.account.UpdateProfileRequest(about=bio))
        await edit_delete(event, "`تم تغيير بايو الـحـسـاب ♥️🧸`")
    except Exception as e:
        await edit_or_reply(event, f"**خطأ:**\n`{e}`")


@catub.cat_cmd(
    pattern="وضع اسم ([\s\S]*)",
    command=("pname", plugin_category),
    info={
        "header": "To set/change name for this account.",
        "usage": ["{tr}pname firstname ; last name", "{tr}pname firstname"],
    },
)
async def _(event):
    "لتعيين / تغيير الاسم لهذا الحساب."
    names = event.pattern_match.group(1)
    first_name = names
    last_name = ""
    if ";" in names:
        first_name, last_name = names.split(";", 1)
    try:
        await event.client(
            functions.account.UpdateProfileRequest(
                first_name=first_name, last_name=last_name
            )
        )
        await edit_delete(event, "`تم تغيير اسم الـحـسـاب ♥️🧸`")
    except Exception as e:
        await edit_or_reply(event, f"**خطأ:**\n`{e}`")


@catub.cat_cmd(
    pattern="وضع صورة$",
    command=("ppic", plugin_category),
    info={
        "header": "To set profile pic for this account.",
        "usage": "{tr}ppic <reply to image or gif>",
    },
)
async def _(event):
    "To set profile pic for this account."
    reply_message = await event.get_reply_message()
    catevent = await edit_or_reply(
        event, "`تحميل صورة الملف الشخصي على بلدي المحلي ...`"
    )
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    photo = None
    try:
        photo = await event.client.download_media(
            reply_message, Config.TMP_DOWNLOAD_DIRECTORY
        )
    except Exception as e:
        await catevent.edit(str(e))
    else:
        if photo:
            await catevent.edit("`الآن ، تحميل إلى تليكرام ...`")
            if photo.endswith((".mp4", ".MP4")):
                # https://t.me/tgbetachat/324694
                size = os.stat(photo).st_size
                if size > 2097152:
                    await catevent.edit("`يجب أن يكون الحجم أقل من 2 ميغا بايت`")
                    os.remove(photo)
                    return
                catpic = None
                catvideo = await event.client.upload_file(photo)
            else:
                catpic = await event.client.upload_file(photo)
                catvideo = None
            try:
                await event.client(
                    functions.photos.UploadProfilePhotoRequest(
                        file=catpic, video=catvideo, video_start_ts=0.01
                    )
                )
            except Exception as e:
                await catevent.edit(f"**خطأ:**\n`{e}`")
            else:
                await edit_or_reply(
                    catevent, "`تم تغيير صورة الـحـسـاب ♥️🧸`"
                )
    try:
        os.remove(photo)
    except Exception as e:
        LOGS.info(str(e))


@catub.cat_cmd(
    pattern="اسم المستخدم ([\s\S]*)",
    command=("pusername", plugin_category),
    info={
        "header": "To set/update username for this account.",
        "usage": "{tr}pusername <new username>",
    },
)
async def update_username(event):
    """For .username command, set a new username in Telegram."""
    newusername = event.pattern_match.group(1)
    try:
        await event.client(UpdateUsernameRequest(newusername))
        await edit_delete(event, USERNAME_SUCCESS)
    except UsernameOccupiedError:
        await edit_or_reply(event, USERNAME_TAKEN)
    except Exception as e:
        await edit_or_reply(event, f"**خطأ:**\n`{e}`")


@catub.cat_cmd(
    pattern="عدد$",
    command=("count", plugin_category),
    info={
        "header": "To get your profile stats for this account.",
        "usage": "{tr}count",
    },
)
async def count(event):
    """لأمر .count ، احصل على إحصائيات الملف الشخصي."""
    u = 0
    g = 0
    c = 0
    bc = 0
    b = 0
    result = ""
    catevent = await edit_or_reply(event, "`Processing..`")
    dialogs = await event.client.get_dialogs(limit=None, ignore_migrated=True)
    for d in dialogs:
        currrent_entity = d.entity
        if isinstance(currrent_entity, User):
            if currrent_entity.bot:
                b += 1
            else:
                u += 1
        elif isinstance(currrent_entity, Chat):
            g += 1
        elif isinstance(currrent_entity, Channel):
            if currrent_entity.broadcast:
                bc += 1
            else:
                c += 1
        else:
            LOGS.info(d)

    result += f"`المستخدمين:`\t**{u}**\n"
    result += f"`الكروبات:`\t**{g}**\n"
    result += f"`الكروبات العامة:`\t**{c}**\n"
    result += f"`القنوات:`\t**{bc}**\n"
    result += f"`البوتات:`\t**{b}**"

    await catevent.edit(result)


@catub.cat_cmd(
    pattern="مسح صورة ?([\s\S]*)",
    command=("delpfp", plugin_category),
    info={
        "header": "To delete profile pic for this account.",
        "description": "If you havent mentioned no of profile pics then only 1 will be deleted.",
        "usage": ["{tr}delpfp <no of pics to be deleted>", "{tr}delpfp"],
    },
)
async def remove_profilepic(delpfp):
    """For .delpfp command, delete your current profile picture in Telegram."""
    group = delpfp.text[8:]
    if group == "all":
        lim = 0
    elif group.isdigit():
        lim = int(group)
    else:
        lim = 1
    pfplist = await delpfp.client(
        GetUserPhotosRequest(user_id=delpfp.sender_id, offset=0, max_id=0, limit=lim)
    )
    input_photos = [
        InputPhoto(
            id=sep.id,
            access_hash=sep.access_hash,
            file_reference=sep.file_reference,
        )
        for sep in pfplist.photos
    ]
    await delpfp.client(DeletePhotosRequest(id=input_photos))
    await edit_delete(
        delpfp, f"`تم مسح {len(input_photos)} صورة الحساب ♥️🧸(s).`"
    )


@catub.cat_cmd(
    pattern="أسماء المستخدمين الخاصة بي$",
    command=("myusernames", plugin_category),
    info={
        "header": "To list public channels or groups created by this account.",
        "usage": "{tr}myusernames",
    },
)
async def _(event):
    "لسرد جميع القنوات والمجموعات العامة."
    result = await event.client(GetAdminedPublicChannelsRequest())
    output_str = "**Your current reserved usernames are:**\n" + "".join(
        f" - {channel_obj.title} @{channel_obj.username} \n"
        for channel_obj in result.chats
    )
    await edit_or_reply(event, output_str)
