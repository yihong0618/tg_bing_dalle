import argparse
import os
import random

import telebot
from BingImageCreator import ImageGen

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tg_token", help="tg token")
    parser.add_argument("bing_cookie", help="bing cookie")
    options = parser.parse_args()
    bot = telebot.TeleBot(options.tg_token)
    bing_cookie = options.bing_cookie
    if not os.path.exists("tg_images"):
        os.mkdir("tg_images")

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
        bot.reply_to(message, "Using bing DALL-E 3 generating images please wait")
        images = i.get_images(s)
        i.save_images(images, path)
        images_count = len(list(os.listdir(path)))
        print(images_count)
        index = random.randint(images_count - len(images), images_count - 1)
        with open(os.path.join(path, str(index)) + ".jpeg", "rb") as f:
            bot.send_photo(message.chat.id, f, reply_to_message_id=message.message_id)
        return

    @bot.message_handler(func=reply_dalle_image)
    def handle(message):
        pass

    def main():
        bot.infinity_polling()

    main()
