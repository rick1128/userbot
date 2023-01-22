# Credits of Plugin @ViperAdnan and @mrconfused(revert)[will add sql soon]
import html

from telethon.tl import functions
from telethon.tl.functions.users import GetFullUserRequest

from ..Config import Config
from ..sql_helper.globals import gvarstatus
from . import ALIVE_NAME, BOTLOG, BOTLOG_CHATID, catub, edit_delete, get_user_from_event

plugin_category = "utils"
DEFAULTUSER = gvarstatus("FIRST_NAME") or ALIVE_NAME
DEFAULTUSERBIO = (
    gvarstatus("DEFAULT_BIO") or "sıɥʇ ǝpoɔǝp uǝɥʇ llıʇu∩ ˙ǝɔɐds ǝʇɐʌıɹd ǝɯos ǝɯ ǝʌı⅁"
)


@catub.cat_cmd(
    pattern="انتحال(?:\s|$)([\s\S]*)",
    command=("انتحال", plugin_category),
    info={
        "header": "لانتحال اي شخص برد على رسالته",
        "usage": "{tr}انتحال <username/userid/reply>",
    },
)
async def _(event):
    "To clone account of mentiond user or replied user"
    replied_user, error_i_a = await get_user_from_event(event)
    if replied_user is None:
        return
    user_id = replied_user.id
    profile_pic = await event.client.download_profile_photo(user_id, Config.TEMP_DIR)
    first_name = html.escape(replied_user.first_name)
    if first_name is not None:
        first_name = first_name.replace("\u2060", "")
    last_name = replied_user.last_name
    if last_name is not None:
        last_name = html.escape(last_name)
        last_name = last_name.replace("\u2060", "")
    if last_name is None:
        last_name = "⁪⁬⁮⁮⁮⁮ ‌‌‌‌"
    replied_user = (await event.client(GetFullUserRequest(replied_user.id))).full_user
    user_bio = replied_user.about
    if user_bio is not None:
        user_bio = replied_user.about
    await event.client(functions.account.UpdateProfileRequest(first_name=first_name))
    await event.client(functions.account.UpdateProfileRequest(last_name=last_name))
    await event.client(functions.account.UpdateProfileRequest(about=user_bio))
    try:
        pfile = await event.client.upload_file(profile_pic)
    except Exception as e:
        return await edit_delete(event, f"**Failed to clone due to error:**\n__{e}__")
    await event.client(functions.photos.UploadProfilePhotoRequest(pfile))
    await edit_delete(event, "**LET US BE AS ONE**")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#الانتحال\nتم بنجاح انتحال [{first_name}](tg://user?id={user_id })",
        )


@catub.cat_cmd(
    pattern="اعادة$",
    command=("اعادة", plugin_category),
    info={
        "header": "لاعادة حسابك قبل الانتحال",
        "note": "For proper Functioning of this command you need to set DEFAULT_USER in Database",
        "usage": "{tr}اعادة",
    },
)
async def revert(event):
    "To reset your original details"
    firstname = DEFAULTUSER
    lastname = gvarstatus("LAST_NAME") or ""
    bio = DEFAULTUSERBIO
    await event.client(
        functions.photos.DeletePhotosRequest(
            await event.client.get_profile_photos("me", limit=1)
        )
    )
    await event.client(functions.account.UpdateProfileRequest(about=bio))
    await event.client(functions.account.UpdateProfileRequest(first_name=firstname))
    await event.client(functions.account.UpdateProfileRequest(last_name=lastname))
    await edit_delete(event, "تم بنجاح اعادة حسابك 🧸❤️")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#الاعادة\nتم بنجاح اعادة حسابك الى قبل الانتحال",
        )
