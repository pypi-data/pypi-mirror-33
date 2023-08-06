# Filename: openhandlers.py

import traceback
import tornado.web

from cg_tornado.common.security import CgSecurity
from cg_tornado.errors import HttpErrors


class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        super().prepare()

        self.gdb = None
        self.User = None

        # URL Format
        # https://demo.codegini.com/<slug>/api/<table>/(.*) -> API Handler
        # https://demo.codegini.com/<slug>/(.*) -> Web Handler

        parts = self.request.uri.split('/')
        if len(parts) < 3:
            raise tornado.web.HTTPError(400)

        slug = parts[1]
        if not slug.startswith('~'):
            raise tornado.web.HTTPError(501)
        slug = slug[1:]
        if slug not in self.application.LoadedProjects:
            raise tornado.web.HTTPError(501)

        self.ProjectSlug = slug
        self.UrlParts = parts
        self.Project = self.application.LoadedProjects[slug]

        try:
            self.gdb = self.Project.GetDbSession()
        except Exception:
            traceback.print_exc()
            raise tornado.web.HTTPError(503)

        self._checkUserSession()
        self.set_header("Server", self.application.ServerName)
        return

    def on_finish(self):
        if self.gdb is not None:
            self.gdb.close()

        super().on_finish()
        return

    def _dispatch(self):
        func = None

        if self.request.uri.endswith('/'):
            func = getattr(self, 'Index', None)
        else:
            path = self.request.uri.split('?')[0]
            method = path.split('/')[-1]

            if method not in self.PublicMethods:
                raise tornado.web.HTTPError(404)

            func = getattr(self, method, None)

        if not func:
            raise tornado.web.HTTPError(404)

        return func()

    def _checkUserSession(self):
        self.authToken = self.request.headers.get('Authorization')
        if self.authToken is None:
            self.authToken = self.get_secure_cookie(self.Project.AuthCookieName)

        self.User = None
        sessionId = None
        if self.authToken is not None:
            try:
                sessionId = CgSecurity.OpenToken(self.authToken, self.application.PrivateKey,
                                                 self.application.PrivateKey_Secret)
            except Exception:
                traceback.print_exc()
                self.clear_all_cookies()
                raise tornado.web.HTTPError(401)

        if sessionId is not None:
            self.User = self._decodeSession(sessionId)

        return

    def _decodeSession(self, sessionId):
        query = self.gdb.query(self.Project.Models.AuthSession).filter(self.Project.Models.AuthSession.session_id == sessionId)
        session = query.one_or_none()
        if session is None:
            print("Session '{}' not found".format(sessionId))
            return None

        user = {
            'user_id': session.user_id,
            # 'first_name': None if session.user.profile is None else session.user.profile.first_name,
            # 'last_name': None if session.user.profile is None else session.user.profile.last_name,
            'email': session.user.email,
            'session_id': sessionId,
            # 'profile_id': None if session.user.profile is None else session.user.profile.profile_id,
        }

        # user['groups'] = (session.user.primary_group, )

        return user

    def AddToMailQueue(self, mailType, recipientEmail, recipientName, data):
        # cgMQ = MailQueue()
        # cgMQ.mail_type = mailType
        # cgMQ.recipient_email = recipientEmail
        # cgMQ.recipient_name = recipientName
        # cgMQ.mail_data = json.dumps(data)
        # cgMQ.date_added = func.unix_timestamp()
        # self.gdb.add(cgMQ)

        # self.gdb.commit()
        return


class BaseWebHandler(BaseHandler):
    def prepare(self):
        super().prepare()

        self.set_header("Content-Type", "text/html;charset=utf-8")
        return

    def get(self, kwargs=None, kwargs2=None):
        return self._dispatch()

    def write_error(self, status_code, **kwargs):
        code = '{}'.format(status_code)
        title = "Unknown Error"
        message = "Unknown Error"

        if code in HttpErrors:
            title = HttpErrors[code]['title']
            message = HttpErrors[code]['message']

        self.render('error-page.html', Code=code, Title=title, Message=message)
        return


def VerifyAuthedUser(method):
    def wrapper(*args):
        if args[0].User is None:
            args[0].redirect('/Login')
        else:
            method(*args)
    return wrapper
