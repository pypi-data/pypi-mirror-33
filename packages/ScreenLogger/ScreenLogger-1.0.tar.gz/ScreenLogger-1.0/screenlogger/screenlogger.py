#!/usr/bin/python3

import logging
import time

LOGFORMAT = "%(asctime)s %(levelname)s - %(message)s - %(pathname)s"
logging.basicConfig(filename = "error.log", level = logging.ERROR, format = LOGFORMAT)
logger = logging.getLogger()

class Msg:

    def __init__(self, mode=None):
        self.mode = mode

    def message(self, msg):
        if self.mode != "quiet":
            print (msg)
        logger.info(msg)
        time.sleep(0.05)

    def error_message(self, msg):
        if self.mode != "quiet":
            print (msg)
        logger.error(msg)
        time.sleep(0.05)


# Run as main

if __name__ == "__main__":

    a = msg()
    a.message("Msg class is up and running.")


# EOF
