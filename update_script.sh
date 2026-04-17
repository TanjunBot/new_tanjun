#!/bin/bash

docker run --rm -v $(pwd)/commands/ai/ask_gpt.py:/usr/local/app/commands/ai/ask_gpt.py tanjun-bot-fixed bash -c "cat /usr/local/app/commands/ai/ask_gpt.py"