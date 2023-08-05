#!/usr/bin/python3

import logging
import time
import os


class Msg:


    def __init__(self, filename="error.log",
                        path=None,
                        mode=None):
        self.mode = mode
        if path is None:
            path = (os.path.dirname(
                os.path.abspath(__file__)) 
                + "/" + filename)
        else:
            path = path + "/" + filename
        LOGFORMAT = ("%(asctime)s %(levelname)s - "
                    + "%(message)s - %(pathname)s")
        logging.basicConfig(filename = path, 
                            level = logging.ERROR, 
                            format = LOGFORMAT)
        self.logger = logging.getLogger()


    def message(self, msg):
        if self.mode != "quiet":
            print (msg)
        self.logger.info(msg)
        time.sleep(0.05)


    def error_message(self, msg):
        if self.mode != "quiet":
            print (msg)
        self.logger.error(msg)
        time.sleep(0.05)


# EOF
