# tg_bing_dalle

tg bot using bing dalle-3

## Usage

Live Show: https://t.me/c/1941649644/2798

In any chat with the bot, send your message like "prompt: something" or "/prompt something". 

You can set "/prompt" as a bot command (botfather -> edit bot -> edit commands).

## How to

How to make your own DALL-E 3 bing tg bot.

1. Make sure your ip can open https://bing.com/create not jump cn.bing (can use GitHub to login）
2. Use https://bing.com/images/create create a new png, F12 in chrome to get cookie string as bing_cookie

   ***Highly recommanded to use Edge or Chrome to get the cookie. We encountered errors when using cookie got by Firefox.***
3. Get tg token, ask Google or ChatGPT, need get it from [botfather](https://t.me/BotFather) 
4. pip install -r requirements.txt
5. python tg.py '${tg_token}' '${bing_cookie}'

*You can provide multiple cookies, to increase the use limit. see:*
```
usage: tg.py [-h] tg_token bing_cookie [bing_cookie ...]
    
positional arguments:
  tg_token     tg token
  bing_cookie  bing cookie
    
options:
  -h, --help   show this help message and exit
    
```

## Appreciation

- Thank you, that's enough. Just enjoy it.
