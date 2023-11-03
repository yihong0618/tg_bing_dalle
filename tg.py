import argparse
import os
from itertools import cycle
from threading import Thread

import telebot
from BingImageCreator import ImageGen
from telebot.types import InputMediaPhoto

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tg_token", help="tg token")
    parser.add_argument("bing_cookie", help="bing cookie", nargs="+")
    options = parser.parse_args()
    bot = telebot.TeleBot(options.tg_token)
    bot_name = bot.get_me().username
    bing_image_obj_list = [ImageGen(i) for i in options.bing_cookie]
    bing_cookie_cnt = len(bing_image_obj_list)
    for index, image_obj in enumerate(bing_image_obj_list):
        try:
            image_obj.get_limit_left()
        except Exception as e:
            print(f"your {index} cookie is wrong please check error: {str(e)}")
            raise
    bing_cookie_pool = cycle(bing_image_obj_list)

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
        s: str = message.text[len(prefix) :].strip()
        # Remove the first word if it is a @username, because it is part of the command if the bot is in a group chat.
        if s.startswith("@"):
            if not s.startswith(f"@{bot_name} "):
                return
            s = " ".join(s.split(" ")[1:])
        if s == "quota?":
            quota_string = "\n".join(
                [
                    f"Cookie{index} left quota: {v.get_limit_left()}."
                    for index, v in enumerate(bing_image_obj_list)
                ]
            )
            bot.reply_to(
                message,
                f"Quota stats: \nWe have {len(bing_image_obj_list)} cookies\n{quota_string}",
            )
            return
        # Prepare the local folder
        print(f"Message from user id {message.from_user.id}")
        path = os.path.join("tg_images", str(message.from_user.id))
        if not os.path.exists(path):
            os.mkdir(path)

        # Find a cookie within the limit
        within_limit = False
        for _ in range(bing_cookie_cnt):
            image_obj = next(bing_cookie_pool)
            limit = image_obj.get_limit_left()
            if limit > 1:
                within_limit = True
                break

        if not within_limit:
            bot.reply_to(
                message,
                "No cookie is with limit left, will wait a long time and maybe fail",
            )
            # No return here, because we can still use the cookie with no limit left.
        else:
            bot.reply_to(
                message,
                f"Using bing DALL-E 3 generating images please wait, left times we can use: {limit-1}",
            )

        # Generate the images
        try:
            images = image_obj.get_images(s)
        except Exception as e:
            print(str(e))
            bot.reply_to(
                message,
                "Your prompt ban from Bing DALL-E 3, please change it and do not use the same prompt.",
            )
            return
        # Save the images locally
        Thread(target=save_images, args=(image_obj, images, path)).start()
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
            bot.reply_to(message, "Generate images error")

        return

    @bot.message_handler(func=reply_dalle_image)
    def handle(message):
        pass

    def main():
        print("Starting tg bing DALL-E 3 images bot.")
        bot.infinity_polling()

    main()
