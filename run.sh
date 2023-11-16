#!/bin/bash

echo "Checking prerequisites..."

python_bin="./venv/bin/python"
config_file=""

# Function to show usage
usage() {
    echo "Usage: $0 [-c <config_file>]"
    exit 1
}

# Parse command-line options
while getopts ":c:" opt; do
  case ${opt} in
    c ) config_file=$OPTARG
      ;;
    \? ) usage
      ;;
  esac
done

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

# Building and running
python_cmd="${python_bin} -u tg.py '$tg_token' $bing_cookies"
# Load configurations from config file if specified
if [ -n "$config_file" ]; then
  python_cmd="${python_cmd} -c '$config_file'"
fi
echo "Ready to run..."
eval $python_cmd
