#!/usr/bin/env python3
"""Notify a message to a Telegram chat using a bot.

Example configuration (~/.config/telegram-notify/config.json):
{
    "token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "chatid": "1234567890"
}

To get the token, create a bot with https://telegram.me/botfather.
To get the chatid, send a message to the bot and open the URL:
https://api.telegram.org/bot<token>/getUpdates
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

level_emojis = {
    "info": "ℹ️",
    "warning": "⚠️",
    "error": "❌",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "message_file",
        type=argparse.FileType(),
        nargs="?",
        default=sys.stdin,
        help="The file containing the message to send, or stdin if not provided.",
    )
    parser.add_argument(
        "--level",
        type=str,
        choices=["info", "warning", "error"],
        default="info",
        help="The level of the message (default: %(default)s).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("~/.config/telegram-notify/config.json").expanduser(),
        help="The configuration file (default: %(default)s).",
    )
    args = parser.parse_args()

    config = json.loads(args.config.read_text())
    token = config["token"]
    chat_id = config["chatid"]

    emoji = level_emojis[args.level]
    header = f"{emoji} {args.level.upper()} {emoji}"
    message = args.message_file.read().strip()
    message = f"{header}\n\n{message}"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    encoded_data = urllib.parse.urlencode(data).encode()

    req = urllib.request.Request(url, data=encoded_data)
    urllib.request.urlopen(req)


if __name__ == "__main__":
    main()
