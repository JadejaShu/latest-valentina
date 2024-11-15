# import logging, re, asyncio
# from pyrogram import Client, filters, enums
# from pyrogram.errors import FloodWait
# from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
# from info import CHANNELS, LOG_CHANNEL, ADMINS
# from database.ia_filterdb import save_file
# from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from utils import temp

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# lock = asyncio.Lock()


# @Client.on_message(filters.chat(CHANNELS) & (filters.document | filters.video | filters.audio))         
# async def media(bot, message):
#     for file_type in ("document", "video", "audio"):
#         media = getattr(message, file_type, None)
#         if media is not None: break
#     else: return
#     media.file_type = file_type
#     media.caption = message.caption
#     await save_file(media)



# @Client.on_callback_query(filters.regex(r'^index'))
# async def index_files(bot, query):
#     if query.data.startswith('index_cancel'):
#         temp.CANCEL = True
#         return await query.answer("Cᴀɴᴄᴇʟʟɪɴɢ Iɴᴅᴇxɪɴɢ", show_alert=True)
        
#     perfx, chat, lst_msg_id = query.data.split("#")
#     if lock.locked():
#         return await query.answer('Wᴀɪᴛ Uɴᴛɪʟ Pʀᴇᴠɪᴏᴜs Pʀᴏᴄᴇss Cᴏᴍᴘʟᴇᴛᴇ', show_alert=True)
#     msg = query.message
#     button = InlineKeyboardMarkup([[
#         InlineKeyboardButton('🚫 ᴄᴀɴᴄᴇʟʟ', "index_cancel")
#     ]])
#     await msg.edit("ɪɴᴅᴇxɪɴɢ ɪs sᴛᴀʀᴛᴇᴅ ✨", reply_markup=button)                        
#     try: chat = int(chat)
#     except: chat = chat
#     await index_files_to_db(int(lst_msg_id), chat, msg, bot)


# @Client.on_message((filters.forwarded | (filters.regex("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text ) & filters.private & filters.incoming & filters.user(ADMINS))
# async def send_for_index(bot, message):
#     if message.text:
#         regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
#         match = regex.match(message.text)
#         if not match: return await message.reply('Invalid link')
#         chat_id = match.group(4)
#         last_msg_id = int(match.group(5))
#         if chat_id.isnumeric(): chat_id  = int(("-100" + chat_id))
#     elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
#         last_msg_id = message.forward_from_message_id
#         chat_id = message.forward_from_chat.username or message.forward_from_chat.id
#     else: return
#     try: await bot.get_chat(chat_id)
#     except ChannelInvalid: return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')
#     except (UsernameInvalid, UsernameNotModified): return await message.reply('Invalid Link specified.')
#     except Exception as e: return await message.reply(f'Errors - {e}')
#     try: k = await bot.get_messages(chat_id, last_msg_id)
#     except: return await message.reply('Make Sure That Iam An Admin In The Channel, if channel is private')
#     if k.empty: return await message.reply('This may be group and iam not a admin of the group.')
#     buttons = InlineKeyboardMarkup([[
#         InlineKeyboardButton('✨ ʏᴇꜱ', callback_data=f'index#{chat_id}#{last_msg_id}')
#         ],[
#         InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ', callback_data='close_data')
#     ]])               
#     await message.reply(f'Do You Want To Index This Channel/ Group ?\n\nChat ID/ Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>', reply_markup=buttons)
    

# @Client.on_message(filters.command('setskip') & filters.user(ADMINS))
# async def set_skip_number(bot, message):
#     if len(message.command) == 2:
#         try: skip = int(message.text.split(" ", 1)[1])
#         except: return await message.reply("Skip Number Should Be An Integer.")
#         await message.reply(f"Successfully Set Skip Number As {skip}")
#         temp.CURRENT = int(skip)
#     else:
#         await message.reply("Give Me A Skip Number")


# async def index_files_to_db(lst_msg_id, chat, msg, bot):
#     total_files = 0
#     duplicate = 0
#     errors = 0
#     deleted = 0
#     no_media = 0
#     unsupported = 0
#     async with lock:
#         try:
#             current = temp.CURRENT
#             temp.CANCEL = False
#             async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
#                 if temp.CANCEL:
#                     await msg.edit(f"Successfully Cancelled!!\n\nSaved <code>{total_files}</code> files to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>")
#                     break
#                 current += 1
#                 if current % 100 == 0:
#                     can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
#                     reply = InlineKeyboardMarkup(can)
#                     try:
#                         await msg.edit_text(text=f"Total Messages Fetched: <code>{current}</code>\nTotal Messages Saved: <code>{total_files}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>", reply_markup=reply)       
#                     except FloodWait as t:
#                         await asyncio.sleep(t.value)
#                         await msg.edit_text(text=f"Total Messages Fetched: <code>{current}</code>\nTotal Messages Saved: <code>{total_files}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>", reply_markup=reply)                          
#                 if message.empty:
#                     deleted += 1
#                     continue
#                 elif not message.media:
#                     no_media += 1
#                     continue
#                 elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
#                     unsupported += 1
#                     continue
#                 media = getattr(message, message.media.value, None)
#                 if not media:
#                     unsupported += 1
#                     continue
#                 media.file_type = message.media.value
#                 media.caption = message.caption
#                 aynav, vnay = await save_file(media)
#                 if aynav:
#                     total_files += 1
#                 elif vnay == 0:
#                     duplicate += 1
#                 elif vnay == 2:
#                     errors += 1       
#         except Exception as e:
#             logger.exception(e)
#             await msg.edit(f'Error: {e}')
#         else:
#             await msg.edit(f'Succesfully Saved <code>{total_files}</code> To Database!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media Messages Skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>')





import logging
import re
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import save_file
from info import CHANNELS, LOG_CHANNEL, ADMINS
from utils import temp

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
lock = asyncio.Lock()

# Handle media messages
@Client.on_message(filters.chat(CHANNELS) & (filters.document | filters.video | filters.audio))
async def media_handler(bot, message):
    try:
        media = next((getattr(message, t, None) for t in ("document", "video", "audio") if getattr(message, t, None)), None)
        if not media:
            return
        media.file_type = message.media.value
        media.caption = message.caption
        await save_file(media)
        logger.info(f"Media saved: {media.file_id}")
    except Exception as e:
        logger.error(f"Error saving media: {e}")
        await message.reply_text(f"Error occurred: {e}")

# Handle callback queries
@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    try:
        if query.data.startswith('index_cancel'):
            temp.CANCEL = True
            return await query.answer("Indexing cancelled", show_alert=True)
        
        _, chat, last_msg_id = query.data.split("#")
        if lock.locked():
            return await query.answer("Previous process still running", show_alert=True)
        
        msg = query.message
        button = InlineKeyboardMarkup([[InlineKeyboardButton('🚫 Cancel', "index_cancel")]])
        await msg.edit("Indexing started...", reply_markup=button)
        chat = int(chat) if chat.isdigit() else chat
        await index_files_to_db(int(last_msg_id), chat, msg, bot)
    except Exception as e:
        logger.error(f"Error in callback query: {e}")
        await query.message.edit_text(f"Error occurred: {e}")

# Fetch messages for indexing
async def index_files_to_db(last_msg_id, chat_id, msg, bot):
    try:
        total_files = duplicate = errors = deleted = no_media = unsupported = 0
        temp.CURRENT = 0
        async with lock:
            async for message in bot.iter_messages(chat_id, last_msg_id):
                if temp.CANCEL:
                    break
                temp.CURRENT += 1
                if message.empty:
                    deleted += 1
                    continue
                if not message.media:
                    no_media += 1
                    continue
                if message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
                    unsupported += 1
                    continue
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                media.file_type = message.media.value
                media.caption = message.caption
                success, error_type = await save_file(media)
                if success:
                    total_files += 1
                elif error_type == 0:
                    duplicate += 1
                elif error_type == 2:
                    errors += 1
            await msg.edit_text(f"Indexing completed:\n"
                                f"Total saved: {total_files}\n"
                                f"Duplicates: {duplicate}\n"
                                f"Deleted: {deleted}\n"
                                f"No Media: {no_media}\n"
                                f"Unsupported: {unsupported}\n"
                                f"Errors: {errors}")
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        await msg.edit_text(f"Error occurred: {e}")

# Command to set skip number
@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    try:
        if len(message.command) != 2:
            return await message.reply("Usage: /setskip <number>")
        temp.CURRENT = int(message.command[1])
        await message.reply(f"Skip number set to {temp.CURRENT}")
    except ValueError:
        await message.reply("Please provide a valid integer.")

# Entry point
if __name__ == "__main__":
    app = Client("my_bot")
    app.run()
