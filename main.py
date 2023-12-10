# Source code Bot Telegram đơn giản sử dụng reCAPTCHA check người dùng dựa trên ChatGPT

import random
from io import BytesIO
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from captcha.image import ImageCaptcha

# Thay 'BOT_TOKEN' với token bot từ BotFather
TOKEN = 'BOT_TOKEN'

user_captchas = {}

def start(update: Update, context: CallbackContext) -> None:
    success_message = update.message.reply_photo(
                photo=open('hihi.jpg', 'rb'),  # # Thay bằng ảnh khác, Ví dụ ở đây là cái ảnh hihi
                caption='Hello there! I am *...*. Type /captcha to do the reCAPTCHA.\n\n_This bot belongs to ..._', # Thay ... bằng cái gì bạn tuỳ chọn
                parse_mode='Markdown'
            )

def generate_captcha() -> tuple[str, BytesIO]:
    captcha_value = ''.join(random.choice('ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjklmnpqrstuvwxyz123456789') for _ in range(4)) # Số ký tự của captcha, ví dụ ở đây là 4
    # Tạo ảnh đính kèm khi giải mã captcha thành công
    captcha_image = ImageCaptcha()
    
    image_data = captcha_image.generate(captcha_value)
    
    image_bytesio = BytesIO(image_data.read())
    image_bytesio.name = 'captcha.png'  

    return captcha_value, image_bytesio

def send_captcha(update: Update, context: CallbackContext) -> None:
    captcha_value, image_bytesio = generate_captcha()

    user_id = update.message.from_user.id
    user_captchas[user_id] = {'captcha_value': captcha_value, 'message_id': None}

    sent_message = update.message.reply_photo(photo=image_bytesio, caption='Please type the characters shown in the image. Includes both uppercase and lowercase characters and numbers ')

    # Store the sent message ID for deletion later
    user_captchas[user_id]['message_id'] = sent_message.message_id

def check_captcha(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in user_captchas:
        user_input = update.message.text

        if user_input == user_captchas[user_id]['captcha_value']:
            # User completed the captcha correctly
            success_message = update.message.reply_photo(
                photo=open('hihi.jpg', 'rb'),  # Copy lại ở trên xuống
                caption='reCAPTCHA passed! Join this group fast: [hoangdeptraivc.com](https://hoangdeptraivc.com)\n_This message will automatically disappear in 5 seconds._',
                parse_mode='Markdown'  # Tự xoá sau 5 giây
            )

            # Xoá tin nhắn của cả User lẫn Bot khi nhập
            bot_message_id = user_captchas[user_id]['message_id']
            if bot_message_id:
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=bot_message_id)
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

            # Xóa thông tin liên quan đến một người dùng khỏi cơ sở dữ liệu tạm thời (temporary storage)
            del user_captchas[user_id]
            context.job_queue.run_once(lambda _: context.bot.delete_message(chat_id=update.effective_chat.id, message_id=success_message.message_id), 5)
        else:
            # Nếu nhập sai captcha

            # Xoá tin nhắn của cả User lẫn Bot khi nhập sai
            bot_message_id = user_captchas[user_id]['message_id']
            if bot_message_id:
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=bot_message_id)
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

            # Lặp lại 
            del user_captchas[user_id]

            # Auto gửi lại captcha khi nhập sai
            send_captcha(update, context)
    else:
        update.message.reply_text('Please use /captcha to get a new reCAPTCHA')

def delete_message(context: CallbackContext):
    # Xóa tin nhắn sau một khoảng thời gian nhất định
    context.bot.delete_message(chat_id=context.job.context[1], message_id=context.job.context[2])

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


