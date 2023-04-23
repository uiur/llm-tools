# Usage:
#   poetry run python count_token.py < sample.txt
#
# Description:
#   This script uses TikToken to count the number of tokens in a text.

import tiktoken
import sys

def count_token(text):
  encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
  encoded = encoding.encode(text)

  return len(encoded)

if __name__ == "__main__":
  text = sys.stdin.read()
  count = count_token(text)
  print(count)

