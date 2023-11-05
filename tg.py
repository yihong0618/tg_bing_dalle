import argparse
import os
from itertools import cycle

import openai
from BingImageCreator import ImageGen  # type: ignore
from telebot import TeleBot  # type: ignore
from telebot.types import BotCommand, Message  # type: ignore

from responder import respond_prompt, respond_quota, respond_pro_prompt
from utils import extract_prompt, pro_prompt_by_openai


def main():
    # Init args
    parser = argparse.ArgumentParser()
    parser.add_argument("tg_token", help="tg token")
    parser.add_argument("bing_cookie", help="bing cookie", nargs="+")
    parser.add_argument(
        "--openai_api_key",
        help="openai api key to rewrite prompt",
        nargs="?",
        default=None,
    )
    parser.add_argument(
        "--openai_model",
        help="openai model to use",
        nargs="?",
        default="gpt-3.5-turbo",
        const="",
    )
    parser.add_argument(
        "--api_base",
        nargs="?",
        dest="api_base",
        help="specify base url other than the OpenAI's official API address",
        default=None,
    )
    parser.add_argument(
        "--deployment_id",
        nargs="?",
        dest="deployment_id",
        help="specify deployment id, only used when api_base points to azure",
        default=None,
    )
    parser.add_argument(
        "--proxy",
        nargs="?",
        dest="proxy",
        default=None,
        help="http proxy url like http://localhost:8080",
    )

    options = parser.parse_args()
    print("Arg parse done.")

    # use openai key to prompt pro
    openai_api_key = options.openai_api_key or os.getenv("OPENAI_API_KEY")
    openai_model = options.openai_model
    proxy = options.proxy
    api_base = options.api_base
    deployment_id = options.deployment_id
    print(options.openai_api_key)

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

    @bot.message_handler(commands=["prompt_pro"])
    @bot.message_handler(regexp="^prompt_pro:")
    def prompt_pro_handler(message: Message) -> None:
        s = extract_prompt(message, bot_name)
        if openai_api_key:
            openai.api_key = openai_api_key
            # if we have key we use openai to pro this prompt
            if api_base:
                openai.api_base = api_base
                # if api_base ends with openai.azure.com, then set api_type to azure
                if api_base.endswith(("openai.azure.com/", "openai.azure.com")):
                    openai.api_type = "azure"
                    openai.api_version = "2023-03-15-preview"
                    default_options = {
                        "engine": deployment_id,
                    }
            if proxy:
                openai.proxy = proxy
            try:
                s = pro_prompt_by_openai(s, openai_model)
                respond_pro_prompt(bot, message, s)
            except Exception as e:
                respond_pro_prompt(
                    bot,
                    message,
                    "Something is wrong with your openai things please check cli",
                )
                print(str(e))
        if not s:
            return
        print(f"{message.from_user.id} send prompt: {s}")
        respond_prompt(bot, message, bing_cookie_pool, bing_cookie_cnt, s)

    # Start bot
    print("Starting tg bing DALL-E 3 images bot.")
    bot.infinity_polling()


if __name__ == "__main__":
    main()
