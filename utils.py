import os
from typing import List, Optional, Tuple

import openai
from BingImageCreator import ImageGen  # type: ignore
from telebot.types import Message  # type: ignore


def extract_prompt(message: Message, bot_name: str) -> Optional[str]:
    """
    This function filters messages for prompts.

    a prompt: start with @bot or 'prompt:' or '/prompt ' or '/prompt@bot'

    Returns:
      str: If it is not a prompt, return None. Otherwise, return the trimmed prefix of the actual prompt.
    """
    msg_text: str = message.text.strip()
    if msg_text.startswith("@"):
        if not msg_text.startswith(f"@{bot_name} "):
            return None
        s = msg_text[len(bot_name) + 2 :]
    else:
        start_words = ["prompt:", "/prompt", "prompt_pro:", "/prompt_pro:"]
        prefix = next((w for w in start_words if msg_text.startswith(w)), None)
        if not prefix:
            return None
        s = msg_text[len(prefix) :]
        # If the first word is '@bot_name', remove it as it is considered part of the command when in a group chat.
        if s.startswith("@"):
            if not s.startswith(f"@{bot_name} "):
                return None
        s = " ".join(s.split(" ")[1:])
    return s


def pro_prompt_by_openai(prompt, model="gpt-3.5-turbo"):
    prompt = f"revise `{prompt}` to a DALL-E prompt"
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    res = completion["choices"][0].get("message").get("content").encode("utf8").decode()
    return res


def get_quota(bing_image_obj_list: List[ImageGen]) -> List[Tuple[int, int]]:
    return [(index, v.get_limit_left()) for index, v in enumerate(bing_image_obj_list)]


def save_images(i: ImageGen, images: List[str], path: str) -> None:
    # save the images in another thread call
    print("Running save images")
    i.save_images(images, path)


def prepare_save_images(message: Message) -> str:
    # Prepare the local folder
    print(f"Message from user id {message.from_user.id}")
    path = os.path.join("tg_images", str(message.from_user.id))
    if not os.path.exists(path):
        os.mkdir(path)
    return path
