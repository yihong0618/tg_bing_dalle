# tg_bing_dalle
tg bing dalle-3

## Link Show 

https://t.me/c/1941649644/2798


## How to
如何自己弄一个 DALL-E 3 bing 的 tg bot.
1. 确保自己是美国的 ip 并且保证自己浏览器访问 https://bing.com/create 不跳 bing.cn (可以尝试用 GitHub 登陆）
2. https://github.com/acheong08/BingImageCreator 参考这个项目拿到 bing 的 cookie, 但这里有个注意，不能用最新版需要 0.4.4, pip install BingImageCreator==0.4.4
3. 拿到 tg 的 token, 去 Google 搜索，去问 ChatGPT 都可以，需要在 [botfather](https://t.me/BotFather) 那拿
4. pip install -r requirements.txt
5. python tg.py ${tg_token} ${bing_cookie} 启动

