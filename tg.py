import argparse
import os
from itertools import cycle

from BingImageCreator import ImageGen  # type: ignore
from telebot import TeleBot  # type: ignore
from telebot.types import BotCommand, Message  # type: ignore

from responder import respond_prompt, respond_quota
from utils import extract_prompt

if __name__ == "__main__":
    # Init args
    parser = argparse.ArgumentParser()
    parser.add_argument("tg_token", help="tg token")
    parser.add_argument("bing_cookie", help="bing cookie", nargs="+")
    options = parser.parse_args()
    print("Arg parse done.")

    # Init bot
    bot = TeleBot(options.tg_token)
    bot_name = bot.get_me().username
    bot.delete_my_commands(scope=None, language_code=None)
    bot.set_my_commands(
        commands=[
            BotCommand("prompt", "prompt of dalle-3"),
            BotCommand("quota", "cookie left quota"),
        ],
    )
    print("Bot init done.")

    # Init BingImageCreator
    bing_image_obj_list = [ImageGen(i) for i in options.bing_cookie]
    bing_cookie_cnt = len(bing_image_obj_list)
    for index, image_obj in enumerate(bing_image_obj_list):
        try:
            image_obj.get_limit_left()
        except Exception as e:
            print(f"your {index} cookie is wrong please check error: {str(e)}")
            raise
    bing_cookie_pool = cycle(bing_image_obj_list)
    print("BingImageCreator init done.")

    # Init local folder
    if not os.path.exists("tg_images"):
        os.mkdir("tg_images")
    print("Local folder init done.")

    # Handlers
    @bot.message_handler(commands=["quota"])
    @bot.message_handler(regexp="^quota?")
    def quota_handler(message: Message) -> None:
        print(f"{message.from_user.id} asks quota...")
        respond_quota(bot, message, bing_image_obj_list)

    @bot.message_handler(commands=["prompt"])
    @bot.message_handler(regexp="^prompt:")
    @bot.message_handler(regexp=f"^@{bot_name} ")
    def prompt_handler(message: Message) -> None:
        s = extract_prompt(message, bot_name)
        if not s:
            return
        if s == "quota?":
            quota_handler(message)
            return
        print(f"{message.from_user.id} send prompt: {s}")
        respond_prompt(bot, message, bing_cookie_pool, bing_cookie_cnt, s)

    # Start bot
    print("Starting tg bing DALL-E 3 images bot.")
    bot.infinity_polling()
