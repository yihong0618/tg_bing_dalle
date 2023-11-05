#!/bin/sh

# Load args from files if exist, otherwise env vars
if [ -f "/credentials/.token" ]; then
  tg_token=$(cat /credentials/.token)
fi

if [ -f "/credentials/.cookies" ]; then
  bing_cookies=""
  while read line; do
    if [ -n "$line" ]; then
      bing_cookies="$bing_cookies'${line}' "
    fi
  done < <(grep . /credentials/.cookies)
  bing_cookies="${bing_cookies% }"
fi

# Exec main process
python_cmd="python3 tg.py '$tg_token' $bing_cookies"
eval $python_cmd
