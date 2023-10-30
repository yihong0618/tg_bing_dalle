import argparse
import os
import telebot
from typing import List
from BingImageCreator import ImageGen
from threading import Thread
from itertools import cycle
from telebot.types import InputMediaPhoto


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tg_token", help="tg token")
    parser.add_argument("bing_cookie", help="bing cookie", nargs="+")
    options = parser.parse_args()
    bot = telebot.TeleBot(options.tg_token)
    bing_cookie = cycle(options.bing_cookie)
    bing_cookie_cnt = len(options.bing_cookie)
    
    if not os.path.exists("tg_images"):
        os.mkdir("tg_images")

    def save_images(i, images, path):
        # save the images in another thread call
        print("Running save images")
        i.save_images(images, path)

    def reply_dalle_image(message):
        start_words = ["prompt:", "/prompt"]
        prefix = next((w for w in start_words if message.text.startswith(w)), None)
        if not prefix:
            return
        # Remove the first word if it is a @username, because it is part of the command if the bot is in a group chat.
        s: str = message.text[len(prefix) :].strip()
        if s.startswith("@"):
            s = " ".join(s.split(" ")[1:])
        # Prepare the local folder
        print(message.from_user.id)
        path = os.path.join("tg_images", str(message.from_user.id))
        if not os.path.exists(path):
            os.mkdir(path)

        # Find a cookie within the limit
        within_limit = False
        for _ in range(bing_cookie_cnt):
            i = ImageGen(next(bing_cookie))
            limit = i.get_limit_left()
            if limit > 1:
                within_limit = True
                break
            bot.reply_to(message, "Out of limit. Tring next cookie...")

        if not within_limit:
            bot.reply_to(message, "No cookie is with limit left.")
            # No return here, because we can still use the cookie with no limit left.
        else:
            bot.reply_to(
                message,
                f"Using bing DALL-E 3 generating images please wait, left times we can use: {limit-1}",
            )

        # Generate the images
        try:
            images = i.get_images(s)
        except Exception as e:
            print(str(e))
            bot.reply_to(message, "Ban from Bing DALL-E 3")
            return
        # Save the images locally
        Thread(target=save_images, args=(i, images, path)).start()
        # Send the images
        photos_list = [InputMediaPhoto(i) for i in images]
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
