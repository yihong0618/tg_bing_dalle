import os
import base64
from typing import List, Optional, Tuple

import requests
from openai import OpenAI
from BingImageCreator import ImageGen  # type: ignore
from telebot.types import Message  # type: ignore


def has_quota(message: Message, bot_name: str) -> bool:
    """
    Check whether the message has a quota.

    a quota: @bot_name quota? or quota? or /quota or /quota@bot

    Returns:
      bool: If it has a quota, return True. Otherwise, return False.
    """
    msg_text: str = message.text.strip()
    # @bot_name quota?
    if msg_text.startswith("@"):
        if not msg_text.startswith(f"@{bot_name} "):
            return False
        msg_text = msg_text[len(bot_name) + 2 :]

    start_words = ["quota?", "/quota"]
    prefix = next((w for w in start_words if msg_text.startswith(w)), None)
    if not prefix:
        return False

    s = msg_text[len(prefix) :]
    # /quota@bot
    if s.startswith("@"):
        if s != f"@{bot_name}":
            return False

    return True


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
        start_words = ["prompt:", "/prompt", "prompt_pro:", "/prompt_pro"]
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


def pro_prompt_by_openai(prompt: str, openai_args: dict, client: OpenAI) -> str:
    prompt = f"revise `{prompt}` to a DALL-E prompt"
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}], **openai_args
    )
    res = completion.choices[0].message.content.encode("utf8").decode()
    return res


def _image_to_data_uri(file_path):
    with open(file_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded_image}"


def pro_prompt_by_openai_vision(prompt: str, openai_args: dict, client: OpenAI) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {client.api_key}",
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": _image_to_data_uri("temp.jpg")},
                    },
                ],
            }
        ],
        "max_tokens": 500,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    ).json()
    res = response["choices"][0]["message"]["content"].encode("utf8").decode()
    prompt = f"{prompt} {res}"
    res = pro_prompt_by_openai(prompt, openai_args, client)
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
