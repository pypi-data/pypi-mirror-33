# Filename: baseapihandler.py

import traceback
import tornado.web
import uuid
import random
import string

from sqlalchemy.exc import IntegrityError

from .openhandlers import BaseHandler
from cg_tornado.errors import HttpErrors, CgBaseException, RequiredFieldMissing, ChildRecordExists


class BaseApiHandler(BaseHandler):
    def prepare(self):
        super().prepare()

        self.set_header("Content-Type", "application/json")

        try:
            self.Data = {}
            if hasattr(self.request, 'files') and len(self.request.files) > 0:
                self.File = self.request.files
            elif hasattr(self.request, 'body') and (len(self.request.body) > 0):
                self.Data = tornado.escape.json_decode(self.request.body)

        except Exception:
            traceback.print_exc()
            raise tornado.web.HTTPError(503)

        if not hasattr(self, 'PublicMethods'):
            self.PublicMethods = []

        self.PublicMethods.extend(['List', 'Single', 'Submit', 'Create', 'Update', 'Delete', 'FilterOptions', 'SelectOptions', 'Attach'])
        return

    def GetUniqueId(self):
        return str(uuid.uuid4()).replace("-", "")

    def GetUniqueCode(self):
        return ''.join(random.choice(string.digits) for _ in range(4))

    def _loadApiModel(self, table):
        model = None
        if table == 'users':
            from projects.common.users_api_model import UserApiModel
            model = UserApiModel(self.gdb, self.Project)
        else:
            from projects.common.dbhelper import CgDbHelper
            model = CgDbHelper(self.gdb, self.Project, table)

        return model

    # Utility Methos
    def addColToData(self, column, value):
        if column not in self.Data or self.Data[column] != value:
            self.Data[column] = value

        return

    def addTopOrder(self, column, direction):

        top_orders = [{
            'column': column,
            'dir': direction
        }]

        orders = self.Data['order'] if 'order' in self.Data else {}
        if len(orders) > 0:
            orders = top_orders + orders
        else:
            orders = top_orders

        self.Data['order'] = orders
        return

    def addTopWhere(self, column, value, op='eq'):
        wheres = self.Data['where'] if 'where' in self.Data else {}
        if len(wheres) == 0:
            wheres = {
                'column': column,
                'search': value,
                'op': op
            }
        else:
            wh2 = {
                'group': 'and',
                'children': [{
                    "column": column,
                    "search": value,
                    "op": op
                }],
            }

            wh2['children'].append(wheres)
            wheres = wh2

        self.Data['where'] = wheres
        return

    def get(self, kwargs=None):
        raise tornado.web.HTTPError(404)

    @tornado.gen.coroutine
    def post(self, slug=None, kwargs=None):
        resp = {}
        try:
            retVal = self._dispatch()
            if isinstance(retVal, tornado.concurrent.Future):
                yield retVal

            return
        except IntegrityError as e:
            if self.application.Debug:
                traceback.print_exc()

            resp = {
                'Status': self.application.StatusError,
                'ErrorCode': -3,
                'ErrorMessage': "{}".format(e.orig.msg.split(' (')[0])
            }
        except KeyError as e:
            if self.application.Debug:
                traceback.print_exc()

            resp = {
                'Status': self.application.StatusError,
                'ErrorCode': -3,
                'ErrorMessage': "Field '{}' is required".format(e.args[0])
            }
        except CgBaseException as e:
            if self.application.Debug:
                traceback.print_exc()

            resp = {
                'Status': self.application.StatusError,
                'ErrorCode': e.ErrorCode,
                'ErrorMessage': e.ErrorMessage
            }

            if e.Args is not None:
                for i in range(0, int(len(e.Args) / 2)):
                    resp[e.Args[2 * i]] = e.Args[2 * i + 1]

        self.set_header("Server", self.application.ServerName)
        self.set_header("Content-Type", "application/json")
        self.set_status(200)
        self.write(resp)
        return

    def write_error(self, status_code, **kwargs):
        if 'exc_info' in kwargs:
            ex = kwargs['exc_info'][1]
            if isinstance(ex, CgBaseException):
                resp = {
                    'Status': self.application.StatusError,
                    'ErrorCode': ex.ErrorCode,
                    'ErrorMessage': ex.ErrorMessage
                }

                self.set_status(200)
                self.write(resp)
                return

        message = 'Unknown Error'
        code = '{}'.format(status_code)
        if code in HttpErrors:
            message = '{}-{}'.format(HttpErrors[code]['title'], HttpErrors[code]['message'])

        resp = {
            'Status': self.application.StatusError,
            'ErrorCode': status_code,
            'ErrorMessage': message
        }

        self.set_header("Server", self.application.ServerName)
        self.set_header("Content-Type", "application/json")
        self.write(resp)
        return

    # Utility Methods
    def AssertData(self, *keys):
        for key in keys:
            if key not in self.Data or self.Data[key] is None:
                raise KeyError(key)
        return

    def AssertDataWithCleaning(self, *keyList):
        for key in keyList:
            if key not in self.Data or self.Data[key] is None:
                raise KeyError(key)

        for key in self.Data:
            if not any(key in k for k in keyList):
                self.Data[key] = None
        return

    def FilterResponse(self, model, data):
        out = {k: data[k] for k in model & data.keys()}
        return out

    def SendSuccessResponse(self, data=None, total_records=None, columns=None):
        if self.gdb is not None:
            self.gdb.commit()

        resp = {}
        if data is not None:
            resp['data'] = data
        if total_records is not None:
            resp['total_records'] = total_records
        if columns is not None:
            resp['columns'] = columns

        resp['Status'] = self.application.StatusSuccess

        self.write(resp)
        return

    def SendErrorResponse(self, *response):
        if self.gdb is not None:
            self.gdb.rollback()

        resp = {}
        if response is not None:
            if len(response) == 1:
                resp = response[0]
            else:
                for i in range(0, int(len(response) / 2)):
                    resp[response[2 * i]] = response[2 * i + 1]

        resp['Status'] = self.application.StatusError

        self.write(resp)
        self.finish()
        return

    def _attachFile(self, data):
        FileAttachment = self.Project.Models.FileAttachment
        UserFile = self.Project.Models.UserFile

        query = self.gdb.query(UserFile).filter(UserFile.file_id == data['file_id'])
        file = query.one_or_none()
        file.is_attached = True

        attachment = FileAttachment()
        attachment.file_id = data['file_id']
        attachment.row_id = data['row_id']
        attachment.table_name = self.table.table_name()
        attachment.is_public = data['is_public'] if 'is_public' in data else True

        self.gdb.add(attachment)
        self.gdb.flush()

        return attachment.attachment_id

    # Common Controller Methods
    def List(self, sendResponse=True):
        columns = self.Data['columns'] if 'columns' in self.Data else []
        wheres = self.Data['where'] if 'where' in self.Data else {}
        orders = self.Data['order'] if 'order' in self.Data else []
        limit = self.Data['limit'] if 'limit' in self.Data else None
        offset = self.Data['offset'] if 'offset' in self.Data else None
        searchKey = self.Data['search'] if 'search' in self.Data and self.Data['search'] != '' else None

        columns, data, total = self.table.getList(columns=columns, wheres=wheres, orders=orders, limit=limit, offset=offset, searchKey=searchKey)

        if sendResponse is True:
            self.SendSuccessResponse(data, total_records=total)
        else:
            return columns, data, total

    def Single(self, sendResponse=True):
        if 'oid' not in self.Data:
            raise RequiredFieldMissing('oid')

        data = None
        if 'columns' in self.Data:
            data = self.table.getSingleForColumns(self.Data['oid'], self.Data['columns'])
        else:
            data = self.table.getSingle(self.Data['oid'])

        if 'sections' in self.Data:
            sections = self.Data['sections']
            for refCol in sections:
                table = sections[refCol]['table']
                columns = sections[refCol]['columns']
                model = self._loadApiModel(table)
                rec = model.getSingleForColumns(data[model.PrimaryKey], columns)
                if rec is not None:
                    for k in rec:
                        data[k] = rec[k]

        if 'child' in self.Data:
            child = self.Data['child']
            # Check this
            model = self._loadApiModel(child['slug'])
            where = {'column': child['foreign_key'], 'search': self.Data['oid']}
            cols, records, count = model.getList(columns=[], wheres=where)
            items = []
            for row in records:
                items.append(model.getSingleForColumns(row[model.PrimaryKey], child['columns']))

            data['child_records'] = items

        if sendResponse is True:
            self.SendSuccessResponse(data)
        else:
            return data

        return

    def Create(self, sendResponse=True):
        if 'sections' in self.Data:
            sections = self.Data['sections']
            for refCol in sections:
                table = sections[refCol]['table']
                data = sections[refCol]['data']
                model = self._loadApiModel(table)
                self.Data[refCol] = model.insertRecord(data)

        row_id = self.table.insertRecord(self.Data)

        if 'attachments' in self.Data and isinstance(self.Data['attachments'], list):
            for attachment in self.Data['attachments']:
                attachment['row_id'] = row_id
                self._attachFile(attachment)

        if sendResponse is True:
            self.SendSuccessResponse(row_id)
        else:
            return row_id

        return

    def Update(self, sendResponse=True):
        self.AssertData(self.table.PrimaryKey)

        if 'sections' in self.Data:
            sections = self.Data['sections']
            for refCol in sections:
                table = sections[refCol]['table']
                data = sections[refCol]['data']

                model = self._loadApiModel(table)
                data[refCol] = self.Data[model.PrimaryKey]
                self.Data[refCol] = model.updateRecord(data)

        row_id = self.table.updateRecord(self.Data)

        if sendResponse is True:
            self.SendSuccessResponse(row_id)
        else:
            return row_id
        return

    def Attach(self):
        self.AssertData('file_id', 'row_id')
        row_id = self._attachFile(self.Data)
        self.SendSuccessResponse(row_id)
        return

    def Submit(self, sendResponse=True):
        oid = None

        if self.Data['__status__'] == 'New':
            oid = self.Create(sendResponse=False)
        else:
            oid = self.Update(sendResponse=False)

        data = self.table.getSingle(oid)
        if sendResponse is True:
            self.SendSuccessResponse(data)
        else:
            return data

    def Delete(self):
        if 'oid' not in self.Data:
            raise RequiredFieldMissing('oid')

        try:
            self.table.deleteRecord(self.Data['oid'])
        except IntegrityError:
            raise ChildRecordExists()

        self.SendSuccessResponse()
        return

    def FilterOptions(self):
        searchKey = self.Data['search'] if 'search' in self.Data and self.Data['search'] != '' else None
        wheres = self.Data['where'] if 'where' in self.Data else {}
        columns = [self.Data['column']]
        orders = self.Data['order'] if 'order' in self.Data else [{"column": "{}".format(columns[0]), "dir": "asc"}]
        self.addTopWhere(columns[0], None, 'ne')

        columns, values, total = self.table.getList(columns=columns, wheres=wheres, orders=orders, limit=25, searchKey=searchKey, distinct=True, linear=True, noCount=True)

        data = [{'value': v[0]} for v in values]

        self.SendSuccessResponse(data)
        return

    def SelectOptions(self):
        columns = self.table.getDropdownColumns()
        primaryKey = self.table.PrimaryKey

        if 'columns' in self.Data and len(self.Data['columns']) > 0:
            columns = self.Data['columns']

        if primaryKey not in columns:
            columns.append(primaryKey)

        orders = self.Data['order'] if 'order' in self.Data else [{"column": "{}".format(columns[0]), "dir": "asc"}]
        searchKey = self.Data['search'] if 'search' in self.Data and self.Data['search'] != '' else None
        wheres = self.Data['where'] if 'where' in self.Data else {}

        columns, data, total = self.table.getList(columns=columns, wheres=wheres, orders=orders, limit=25, searchKey=searchKey, noCount=True)

        for obj in data:
            obj['value'] = obj[columns[0]]
            obj['id'] = obj[self.table.PrimaryKey]

        self.SendSuccessResponse(data)
        return
