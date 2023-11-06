#!/bin/bash

echo "Checking prerequisites..."

python_bin="./venv/bin/python"

# Check if using pyenv
if [[ "$PYENV_VIRTUAL_ENV" ]]; then
  python_bin="python"
  echo "Currently, you are in a virtual environment managed by pyenv..."
  echo "It is assumed that you have already installed the requirements."
  echo "If not, please execute: python -m pip install -r requirements.txt"
# Check if venv exists, create if needed
elif [ ! -f "venv/bin/python" ]; then
  echo "Creating virtual environment and installing requirements..."
  python -m venv venv
  venv/bin/python -m pip install -r requirements.txt
fi

# Check if .token file exists
if [ ! -f ".token" ]; then
  echo "Error: .token file not found"
  exit 1
fi

# Check if .cookies file exists
if [ ! -f ".cookies" ]; then
  echo "Error: .cookies file not found"
  exit 1
fi

echo "Prerequisites look good!"

# Load token from .token file
echo "Loading .token..."
tg_token=$(cat .token)

# Load cookies from .cookies file and concat into string
echo "Loading .cookies..."
bing_cookies=""
while read line; do
  if [ -n "$line" ]; then
    bing_cookies="$bing_cookies'${line}' "
  fi
done < <(grep . .cookies)

# Remove trailing space
bing_cookies="${bing_cookies% }"

# Building and running
python_cmd="${python_bin} tg.py '$tg_token' $bing_cookies"
echo "Ready to run..."
eval $python_cmd
