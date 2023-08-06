# -*- coding: utf-8 -*-

# https://github.com/liris/websocket-client
## sudo pip install --user websocket-client
from websocket import create_connection
import sys
import random


class mailbox(object):
    """10 minute mailbox"""

    def __init__(self):
        super(mailbox, self).__init__()
        self.ws = create_connection("wss://dropmail.me/websocket")
        self.next = self.ws.recv
        self.close = self.ws.close
        self.email = self.next()[1:].split(":")[0]
        self.next()

    def get_email(self):
        self.box = mailbox()
        print(self.box.email)
        return self.box.email

    def get_email_message(self):
        from json import loads
        from datetime import datetime
        result = self.box.next()
        if result:
            print("Recieved following at {0}".format(datetime.now()))
            text = loads(result[1:])
            for key in text:
                message = text[key].replace("\n", "").replace("\r", "").replace(" ", "")
                print(key, message)
            return text


if __name__ == '__main__':
    try:
        box = mailbox()
        box.get_email()
        while True:
            box.get_email_message()
    except KeyboardInterrupt:
        sys.exit(0)
