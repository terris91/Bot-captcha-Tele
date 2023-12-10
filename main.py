# Source code Bot Telegram đơn giản sử dụng reCAPTCHA check người dùng dựa trên ChatGPT

import random
from io import BytesIO
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from captcha.image import ImageCaptcha

# Đổi 'BOT_TOKEN' bằng token bot
TOKEN = '6989035514:AAFVCXvf6x-KkHASuoF-VGI1zqd9MMd8i3A'

# Từ điển lưu trữ giá trị captcha dành riêng cho người dùng
user_captchas = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am x-Hertz Alpha Bot. Type /captcha to do the reCAPTCHA.\n\nThis bot belongs to @IamxHz')

def generate_captcha() -> tuple[str, BytesIO]:
    # Tạo 1 cái captcha random (tự custom lại cũng được)
    captcha_value = ''.join(random.choice('ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjklmnpqrstuvwxyz123456789') for _ in range(4)) #captcha dài 6 ký tự

    
    captcha_image = ImageCaptcha()

    
    image_data = captcha_image.generate(captcha_value)

    
    image_bytesio = BytesIO(image_data.read())
    image_bytesio.name = 'captcha.png'  

    return captcha_value, image_bytesio

def send_captcha(update: Update, context: CallbackContext) -> None:
    # Tạo captcha
    captcha_value, image_bytesio = generate_captcha()


    user_id = update.message.from_user.id
    user_captchas[user_id] = captcha_value

    # Gửi captcha
    update.message.reply_photo(photo=image_bytesio, caption='Please type the characters shown in the image. Includes both uppercase and lowercase characters and numbers ')

def check_captcha(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # Kiểm tra xem người dùng có lưu giá trị hình ảnh xác thực hay không
    if user_id in user_captchas:
        # Get user's input
        user_input = update.message.text

        # So sánh tin nhắn của người dùng với ban đầu
        if user_input == user_captchas[user_id]:
            # Nếu đúng gửi tin nhắn (VD: ở đây là 1 link)
            update.message.reply_text('reCAPTCHA passed! Here is your link: https://hoangdeptraivc.com')
        else:
            update.message.reply_text('Incorrect reCAPTCHA. Please use /captcha to try again.')

        # Xoá captcha sau khi check
        del user_captchas[user_id]
    else:
        update.message.reply_text('Please use /captcha to get a new reCAPTCHA')

def main() -> None:
    updater = Updater(TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("captcha", send_captcha))

    # Add 1 cái MessageHandler để check user input cho reCAPTCHA
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_captcha))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
