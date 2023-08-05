# FatJSON. Written by Jake Gealer <jake@gealer.email> 2018.
# Licensed under the MPL-2.0 license (https://www.mozilla.org/en-US/MPL/2.0/).

import json
import logging
import sys
import pprint

logger = logging.getLogger("FatJSON")
logging.basicConfig(level=logging.INFO)

pp = pprint.PrettyPrinter()


def main(fp):
    logger.info("Loading the JSON...")

    try:
        _json = json.load(open(fp, "r"))
    except BaseException as e:
        logger.error(
            "Unable to open the JSON: {}".format(e)
        )
        return

    logger.info(
        'Successfully loaded the JSON. Type "help" for help.'
    )

    levels = []

    while True:
        text = input("> ")
        text_split = text.split(" ")
        cmd = text_split[0].lower()
        if cmd == "keys":
            if isinstance(_json, dict):
                print(
                    [k for k in _json]
                )
            else:
                logger.error(
                    "The JSON/object selected does not have keys."
                )
        elif cmd == "print":
            try:
                print(_json)
            except BaseException:
                logger.error(
                    "Could not print the JSON/value."
                )
        elif cmd == "pprint":
            try:
                pp.pprint(_json)
            except BaseException:
                logger.error(
                    "Could not pretty print the JSON/value."
                )
        elif cmd == "type":
            print(type(_json).__name__)
        elif cmd == "length":
            try:
                print(len(_json))
            except TypeError:
                logger.error("Could not get length.")
        elif cmd == "goto":
            if isinstance(_json, list):
                try:
                    key = int(text_split[1])
                    levels.append(_json)
                    try:
                        _json = _json[key]
                        logger.info("Gone up a level.")
                    except KeyError:
                        logger.error("Invalid key.")
                except ValueError:
                    logger.error("Invalid key.")
            elif not isinstance(_json, dict):
                logger.error(
                    "This requires a dict-like/list-like object."
                )
            else:
                key = " ".join(text_split[1:])
                if key not in _json:
                    logger.error(
                        "Key not in dict-like object."
                    )
                else:
                    levels.append(_json)
                    _json = _json[key]
                    logger.info(
                        "Gone up a level."
                    )
        elif cmd == "back":
            if len(levels) >= 1:
                _json = levels[-1]
                del levels[-1]
                logger.info(
                    "Gone back a level."
                )
            else:
                logger.error(
                    "You need to go up a level first."
                )
        elif cmd == "exit":
            exit(0)
        elif cmd == "help":
            print("""keys - Lists the keys in a dict-like object.
print - Prints the currently selected object.
pprint - Pretty prints the currently selected object.
type - Shows the type of the currently selected object.
length - Shows the length of the currently selected object.
goto [key] - Selects a key from a dict-like/list-like object.
back - Goes back a level.
exit - Exits the application.""")
        else:
            logger.error(
                'No such command. Run "help" for a command list.'
            )


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        logger.error("No arguments found.")
    else:
        try:
            main(" ".join(args))
        except KeyboardInterrupt:
            pass
