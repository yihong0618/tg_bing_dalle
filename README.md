# tg_bing_dalle

tg bot using bing dalle-3

## Usage

Live Show: https://t.me/c/1941649644/2798

In any chat with the bot, send your message like "prompt: something" or "/prompt something". 

You can set "/prompt" as a bot command (botfather -> edit bot -> edit commands).

## How to

如何自己弄一个 DALL-E 3 bing 的 tg bot.

1. 确保自己是美国的 ip 并且保证自己浏览器访问 https://bing.com/create 不跳 bing.cn (可以尝试用 GitHub 登陆）
2. 在 https://bing.com/create 新建一张图，在 chorme 里拿到 cookie 字符串作为 bing_cookie
3. 拿到 tg 的 token, 去 Google 搜索，去问 ChatGPT 都可以，需要在 [botfather](https://t.me/BotFather) 那拿
4. pip install -r requirements.txt
5. python tg.py '${tg_token}' '${bing_cookie}' 启动

## Appreciation

- Thank you, that's enough. Just enjoy it.
