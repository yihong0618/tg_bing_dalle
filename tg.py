import argparse
import os
from itertools import cycle

from openai import OpenAI, AzureOpenAI
import toml  # type: ignore
from BingImageCreator import ImageGen  # type: ignore
from telebot import TeleBot  # type: ignore
from telebot.types import BotCommand, Message  # type: ignore

from responder import respond_prompt, respond_quota
from utils import (
    extract_prompt,
    pro_prompt_by_openai,
    pro_prompt_by_openai_vision,
    has_quota,
)


def main():
    # Init args
    parser = argparse.ArgumentParser()
    parser.add_argument("tg_token", help="tg token")
    parser.add_argument("bing_cookie", help="bing cookie", nargs="+")
    parser.add_argument(
        "-c",
        dest="CONFIG_FILE",
        help="additional config file",
        default=None,
    )
    options = parser.parse_args()
    print("Arg parse done.")

    # Read config
    config = dict()
    if options.CONFIG_FILE:
        with open(options.CONFIG_FILE) as f:
            config: dict = toml.load(f)
        print("Config parse done.")

    # Setup openai
    openai_client = None

    openai_conf: dict = config.get("openai")
    if openai_conf is not None:
        openai_client = OpenAI(**openai_conf)
        print("OpenAI init done.")

    azure_openai_conf: dict = config.get("azure_openai")
    if azure_openai_conf is not None:
        openai_client = AzureOpenAI(**azure_openai_conf)
        print("Azure OpenAI init done.")

    openai_args = config.get("openai_args", dict())

    # Init bot
    bot = TeleBot(options.tg_token)
    bot_name = bot.get_me().username
    bot.delete_my_commands(scope=None, language_code=None)
    bot.set_my_commands(
        commands=[
            BotCommand("prompt", "prompt of dalle-3"),
            BotCommand("quota", "cookie left quota"),
        ]
        + (
            [BotCommand("prompt_pro", "prompt with GPT enhanced")]
            if openai_client
            else []
        ),
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
    @bot.message_handler(regexp="^quota\?")
    def quota_handler(message: Message) -> None:
        if has_quota(message, bot_name):
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

    @bot.message_handler(content_types=["photo"])
    def prompt_photo_handler(message: Message) -> None:
        s = message.caption
        if not s.startswith("prompt:"):
            return
        if not openai_client:
            bot.reply_to(message, "OpenAI config not found.")
            prompt_handler(message)
            return
        file_path = bot.get_file(message.photo[0].file_id).file_path
        url = "https://api.telegram.org/file/bot{0}/{1}".format(bot.token, file_path)
        try:
            s = pro_prompt_by_openai_vision(s, openai_args, url, openai_client)
            bot.reply_to(message, f"Rewrite image and prompt by GPT Vision: {s}")
        except Exception as e:
            bot.reply_to(message, "Something is wrong when GPT rewriting your prompt.")
            print(str(e))
        print(f"{message.from_user.id} send prompt: {s}")
        respond_prompt(bot, message, bing_cookie_pool, bing_cookie_cnt, s)

    @bot.message_handler(commands=["prompt_pro"])
    @bot.message_handler(regexp="^prompt_pro:")
    def prompt_pro_handler(message: Message) -> None:
        s = extract_prompt(message, bot_name)
        if not s:
            return
        if not openai_client:
            bot.reply_to(message, "OpenAI config not found.")
            prompt_handler(message)
            return

        try:
            s = pro_prompt_by_openai(s, openai_args, openai_client)
            bot.reply_to(message, f"Rewrite by GPT: {s}")
        except Exception as e:
            bot.reply_to(message, "Something is wrong when GPT rewriting your prompt.")
            print(str(e))

        print(f"{message.from_user.id} send prompt: {s}")
        respond_prompt(bot, message, bing_cookie_pool, bing_cookie_cnt, s)

    # Start bot
    print("Starting tg bing DALL-E 3 images bot.")
    bot.infinity_polling()


if __name__ == "__main__":
    main()
