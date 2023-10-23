import argparse
import os
import random

import telebot
from BingImageCreator import ImageGen
from threading import Thread
from telebot.types import InputMediaPhoto, InputMediaVideo


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tg_token", help="tg token")
    parser.add_argument("bing_cookie", help="bing cookie")
    options = parser.parse_args()
    bot = telebot.TeleBot(options.tg_token)
    bing_cookie = options.bing_cookie
    if not os.path.exists("tg_images"):
        os.mkdir("tg_images")

    def save_images(i, images, path):
        # save the images in another thread call
        print("Running save images")
        i.save_images(images, path)

    def reply_dalle_image(message):
        start_words = "prompt:"
        # bot.send_message(message.chat.id, f'{message.chat.id}')
        if not message.text.startswith(start_words):
            return
        print(message.from_user.id)
        path = os.path.join("tg_images", str(message.from_user.id))
        if not os.path.exists(path):
            os.mkdir(path)
        s = message.text[len(start_words) :].strip()
        i = ImageGen(bing_cookie)
        limit = i.get_limit_left()
        if limit < 2:
            bot.reply_to(message, f"We can not use it, cause we have no limit here")
        else:
            bot.reply_to(
                message,
                f"Using bing DALL-E 3 generating images please wait, left times we can use: {limit-1}",
            )
        try:
            images = i.get_images(s)
        except Exception as e:
            print(str(e))
            bot.reply_to(message, "Ban from Bing DALL-E 3")
            return
        photos_list = [InputMediaPhoto(i) for i in images]
        Thread(target=save_images, args=(i, images, path)).start()
        if photos_list:
            bot.send_media_group(
                message.chat.id,
                photos_list,
                reply_to_message_id=message.message_id,
                disable_notification=True,
            )
        else:
            bot.reply_to(message, "Your prompt generate error")

        return

    @bot.message_handler(func=reply_dalle_image)
    def handle(message):
        pass

    def main():
        bot.infinity_polling()

    main()
