# Filename: securehandlers.py

import tornado.web

from .baseapihandler import BaseApiHandler
from .openhandlers import BaseWebHandler


class SecureApiHandler(BaseApiHandler):
    def prepare(self):
        super().prepare()

        if self.User is None:
            self.clear_all_cookies()
            raise tornado.web.HTTPError(401)

        self.table = self.Model(self.gdb)
        return


class SecureWebHandler(BaseWebHandler):
    def prepare(self):
        super().prepare()
        if self.User is None:
            raise tornado.web.HTTPError(401)

        return
