# Source code Bot Telegram đơn giản sử dụng reCAPTCHA check người dùng dựa trên ChatGPT
# Credit: NGUYỄN TRỌNG HOÀNG

# VUi lòng cài phiên bản 13.15 --> pip install python-telegram-bot==13.15

import random

from io import BytesIO
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext 
from captcha.image import ImageCaptcha

# MAIN:

# Thay 'BOT TOKEN' với token bot từ BotFather
TOKEN = 'BOT TOKEN'

user_captchas = {}

def start(update: Update, context: CallbackContext) -> None:
    success_message = update.message.reply_photo(
        photo=open('hihi.jpg', 'rb'),  # Thay bằng ảnh khác, Ví dụ ở đây là cái ảnh hihi
        caption='Hello there! I am *...*. Type /captcha to do the reCAPTCHA.\n\n_This bot belongs to @..._',# Thay ... bằng cái gì bạn tuỳ chọn hoặc ghi gì cũng được
        parse_mode='Markdown'
    )

def generate_captcha() -> tuple[str, BytesIO]:
    captcha_value = ''.join(random.choice('ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjklmnpqrstuvwxyz123456789') for _ in range(4))# Số ký tự của captcha, ví dụ ở đây là 4

    captcha_image = ImageCaptcha()

    image_data = captcha_image.generate(captcha_value)

    image_bytesio = BytesIO(image_data.read())
    image_bytesio.name = 'captcha.png'

    return captcha_value, image_bytesio

def send_captcha(update: Update, context: CallbackContext) -> None:
    captcha_value, image_bytesio = generate_captcha()

    user_id = update.message.from_user.id
    user_captchas[user_id] = {'captcha_value': captcha_value, 'message_id': None}

    # Đoạn này là khúc: Bot sẽ xoá tin nhắn sau khi người dùng gõ "/captcha"
    try:
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

    sent_message = update.message.reply_photo(photo=image_bytesio,
                                              caption='Please type the characters shown in the image. '
                                                      'Includes both uppercase and lowercase characters and numbers ')

    # Lưu trữ ID tin nhắn trên terminal
    user_captchas[user_id]['message_id'] = sent_message.message_id

    print("Captcha sent successfully!")

def check_captcha(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in user_captchas:
        user_input = update.message.text

        if user_input == user_captchas[user_id]['captcha_value']:
            # Khi user hoàn thành captcha
            success_message = update.message.reply_photo(
                photo=open('hihi.jpg', 'rb'),  
                caption='reCAPTCHA passed! Join this group fast: [Hoangdeptrai](https://Hoangdeptrai.com)\n_This message will automatically disappear in 5 seconds._',
                parse_mode='Markdown' # Xoá tin nhắn sau 5 giây
            )

            # Xoá cả tin nhắn bot lẫn người dùng
            bot_message_id = user_captchas[user_id]['message_id']
            if bot_message_id:
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=bot_message_id)
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

            # Xóa mục nhập user_id
            del user_captchas[user_id]

            # Set thời gian xoá tin nhắn (5 giây)
            context.job_queue.run_once(lambda _: context.bot.delete_message(chat_id=update.effective_chat.id,
                                                                            message_id=success_message.message_id), 5)
        else:
            # Khi user nhập sai captcha

            # Gửi tin nhắn Incorrect captcha. Please try again!
            error_message = update.message.reply_text('Incorrect captcha. Please try again!')

            # Xoá tin nhắn "Incorrect captcha. Please try again!" sau 1 giây
            bot_message_id = user_captchas[user_id]['message_id']
            if bot_message_id:
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=bot_message_id)
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

            # Tiếp tục xoá user_id
            del user_captchas[user_id]

            # Delete sau 1 giây
            context.job_queue.run_once(lambda _: context.bot.delete_message(chat_id=update.effective_chat.id,
                                                                            message_id=error_message.message_id), 1)

            # Captcha mới
            send_captcha(update, context)
    else:
        update.message.reply_text('Please use /captcha to get a new reCAPTCHA')

def main() -> None:
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("captcha", send_captcha))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_captcha))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
