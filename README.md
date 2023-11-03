# tg_bing_dalle

Telegram bot using bing dalle-3

## Usage

Live Show: https://t.me/c/1941649644/2798

In any chat with the bot, send your message like "prompt: something" or "/prompt something".
You can also send your message like "prompt: quota?" to get the limit.

You can set "/prompt" as a bot command (botfather -> edit bot -> edit commands).

## How to

How to make your own DALL-E 3 bing tg bot.

1. Make sure your ip can open https://bing.com/create not jump cn.bing (can use GitHub to login）
2. Use https://bing.com/images/create create a new png, F12 in chrome to get cookie string as bing_cookie

   **_Highly recommanded to use Edge or Chrome to get the cookie, and don't use incognito/privacy mode. We encountered errors when using cookie got by Firefox._**

3. Get tg token, ask Google or ChatGPT, need get it from [botfather](https://t.me/BotFather)
4. pip install -r requirements.txt
5. python tg.py '${tg_token}' '${bing_cookie}'

Or you can use docker to run it:
1. docker build -t tg_bing_dalle .
2. docker run -d --name tg_bing_dalle -e tg_token='${tg_token}' -e bing_cookie='${bing_cookie}' -network host tg_bing_dalle

*You can provide multiple cookies, to increase the use limit. see:*

```
usage: tg.py [-h] tg_token bing_cookie [bing_cookie ...]

positional arguments:
  tg_token     tg token
  bing_cookie  bing cookie

options:
  -h, --help   show this help message and exit

```

## Contribution

- Any issues PR welcome.
- Any other bot type like slack/discord welcome

## Deploy to Fly.io

1. Install [flyctl](https://fly.io/docs/getting-started/installing-flyctl/)
2. `flyctl auth login`
3. `flyctl launch`
   > [!NOTE]
   > Change the app name to your own name in fly.toml
4. `flyctl secrets set tg_token=`_your tg_token_
5. `flyctl secrets set bing_cookie=`_your bing_cookie_
6. `flyctl deploy`

## Appreciation

- Thank you, that's enough. Just enjoy it.

