# Filename: dbhelper.py

import traceback

from decimal import Decimal

from sqlalchemy import or_, and_, desc, asc
from sqlalchemy.sql import func
from sqlalchemy.orm import aliased

from cg_tornado.errors import InvalidColumn, TableColumnNotFound, RecordNotFound


class Context():
    def __init__(self, searchKey):
        self.OrWheres = []
        self.Joins = []
        self.SelectedColumns = []
        self.SearchKey = searchKey
        self.JoinRefs = {}


class CgDbHelper:
    def __init__(self, gdb, project, table_name=None):
        self.gdb = gdb

        self.Project = project

        if table_name is not None:
            self.Model = self.Project.Registry[table_name]
            self.PrimaryKey = self.Project.WebAppLoaded['controllers'][table_name]['key']
        else:
            self.Model = None
            self.PrimaryKey = None

        self.EnableAttachment = False
        # self.PrimaryKey = 'not set'
        self.PrimaryKeyType = 'INT'
        self.PrimarykeyAutoIncrement = True
        self.EnableChangeLog = False

    def getVisibleColumns(self):
        return []

    def getDropdownColumns(self):
        return []

    def getRequiredFields(self):
        return []

    def table_name(self):
        return self.Model.__tablename__

    def _addDeletedWhere(self, wheres):
        col = getattr(self.Model, 'is_deleted', None)
        if col is not None:
            if len(wheres) == 0:
                wheres = {
                    'column': 'is_deleted',
                    'search': [0],
                    'op': 'eq'
                }
            else:
                wh2 = {
                    'group': 'and',
                    'children': [{
                        'column': 'is_deleted',
                        'search': [0],
                        'op': 'eq'
                    }],
                }

                wh2['children'].append(wheres)
                wheres = wh2

        return wheres

    def getList(self, columns=[], wheres={}, orders=[], limit=None, offset=None, searchKey=None, groupBy=None, distinct=False, skipDelCheck=False, linear=False, noCount=False):
        if '__status__' in columns:
            columns.remove('__status__')

        if not skipDelCheck:
            wheres = self._addDeletedWhere(wheres)

        if len(columns) == 0:
            columns = self.getVisibleColumns()

        if distinct is False:
            if self.PrimaryKey in columns:
                columns.remove(self.PrimaryKey)

            columns.insert(0, self.PrimaryKey)

        context = Context(searchKey)

        self.CheckColumns(columns, context)

        query = self.gdb.query(*context.SelectedColumns)
        criterias = self._AddWheres(wheres, context)

        if criterias is not None:
            query = query.filter(criterias)

        if len(orders) > 0:
            for order in orders:
                col = self.GetFinalColumn(self.Model, order['column'], context)

                if col is None:
                    raise InvalidColumn(order['column'])

                if str(order['dir']).lower() == "desc":
                    query = query.order_by(desc(col))
                else:
                    query = query.order_by(asc(col))
        # else:
        #     if self.PrimarykeyAutoIncrement is False:
        #         col = self.GetFinalColumn(self.Model, "date_updated", None)
        #     else:
        #         col = self.GetFinalColumn(self.Model, self.PrimaryKey, None)
        #     query = query.order_by(desc(col))

        for j in context.Joins:
            if j['type'] == 'inner':
                query = query.join(j['join'])
            elif j['type'] == 'outer':
                query = query.outerjoin(j['join'])

        if len(context.OrWheres) > 0:
            query = query.filter(or_(*context.OrWheres))

        if groupBy is not None:
            gb_col = self.GetFinalColumn(self.Model, groupBy, context)
            if gb_col is None:
                raise InvalidColumn(groupBy)

            query = query.group_by(gb_col)

        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        if distinct is True:
            query = query.distinct()

        total = 0
        if not noCount:
            total_r = self.gdb.execute(query.statement.with_only_columns([func.count()]).order_by(None).limit(None).offset(None))
            total = total_r.scalar()

        # print("{}".format("~" * 25))
        # print("dbHelper: List\r\n{}".format(str(query.statement.compile(compile_kwargs={"literal_binds": True}))))
        # print("{}".format("~" * 25))

        data = query.all()
        rows = data

        if not linear:
            rows = CgDbHelper._MakeDict(columns, data)

        return (columns, rows, total)

    def processDataSources(self, srcs, formData={}):
        dataSources = {}

        for ds in srcs:
            columns, result_rows, total = self.getFromDataSrc(ds)
            dataSources[ds['name']] = result_rows

        return dataSources

    def getFromDataSrc(self, dataSrc):
        cols = dataSrc['columns']
        where = dataSrc['where']
        groupBy = dataSrc['group_by'] if 'group_by' in dataSrc else None
        dsType = dataSrc['type']
        if 'response_type' not in dataSrc:
            dataSrc['response_type'] = 'list'

        cols_dict = {}
        for c in cols:
            if 'as' in c:
                cols_dict[c['as']] = c
            else:
                cols_dict[c['column']] = c

        if groupBy is not None:
            bFound = False
            for c in cols:
                if c['column'] == groupBy:
                    bFound = True
                    break

            if not bFound:
                cols.append({'column': groupBy, 'func': 'none'})

        check_rows = []
        check_column = None
        check_columns = []
        if groupBy is not None and 'fetch_zero' in dataSrc:
            import codegini.data.api_models as api_models
            api_model = getattr(api_models, dataSrc['fetch_zero']['ApiModel'])
            table2 = api_model(self.gdb)

            check_column = dataSrc['fetch_zero']['check_column']
            bFound = False
            for c in dataSrc['fetch_zero']['columns']:
                if c['column'] == check_column:
                    bFound = True
                    break

            if not bFound:
                dataSrc['fetch_zero']['columns'].append({'column': check_column, 'func': 'none'})

            columns = dataSrc['fetch_zero']['columns']
            check_columns, check_rows = table2.getAggregate(columns=columns)

        if dsType == 'aggr':
            columns, rows = self.getAggregate(columns=cols, wheres=where, groupBy=groupBy)
            total = len(rows)

            result_rows = []
            if groupBy is not None and 'fetch_zero' in dataSrc:
                for cr in check_rows:
                    bFound = False
                    for r in rows:
                        if cr[check_column] == r[groupBy]:
                            bFound = True
                            break
                    if not bFound:
                        r = {}
                        r[groupBy] = cr[check_column]
                        for c in columns:
                            if c in cr:
                                r[c] = cr[c]
                            elif c != groupBy:
                                if cols_dict[c]['func'] == 'none':
                                    r[c] = None
                                else:
                                    r[c] = 0

                    result_rows.append(r)
            else:
                result_rows = rows

            if dataSrc['response_type'] == 'dict':
                if len(result_rows) > 1:
                    mes = 'Expected one result, got {}'.format(total)
                    raise LTBaseException(999, mes)

                result_rows = result_rows[0] if len(result_rows) > 0 else {}

            return columns, result_rows, total

        # if dsType == 'aggr':
        #     columns, rows = self.getAggregate(columns=cols, wheres=where, groupBy=groupBy)
        #     total = len(rows)
        #     return columns, rows, total
        #
        # if dsType == 'aggr':
        #     columns, rows = self.getAggregate(columns=cols, wheres=where, groupBy=groupBy)
        #     total = len(rows)
        #     return columns, rows, total

    def getAggregate(self, columns=[], wheres={}, groupBy=None, skipDelCheck=False, linear=False):
        if '__status__' in columns:
            columns.remove('__status__')

        if not skipDelCheck:
            wheres = self._addDeletedWhere(wheres)

        if len(columns) == 0:
            return None

        context = Context(None)
        resultColumns = []

        allRelations = self.Model.__mapper__.relationships._data.keys()

        for col2 in columns:
            if 'func' not in col2:
                col2['func'] = 'none'

            col = col2['column']
            if 'as' in col2:
                resultColumns.append(col2['as'])
            else:
                resultColumns.append(col)

            if col in allRelations and '.' not in col:
                raise InvalidColumn(col)

            column = self.GetFinalColumn(self.Model, col, context)
            if column is None:
                raise InvalidColumn(col)

            aggrCol = None
            if col2['func'].lower() == 'sum':
                aggrCol = func.sum(column)
            elif col2['func'].lower() == 'avg':
                aggrCol = func.avg(column)
            elif col2['func'].lower() == 'min':
                aggrCol = func.min(column)
            elif col2['func'].lower() == 'max':
                aggrCol = func.max(column)
            elif col2['func'].lower() == 'count':
                aggrCol = func.count(column)
            elif col2['func'].lower() == 'none':
                aggrCol = column

            if aggrCol is None:
                raise InvalidColumn('{} for {}'.format(col2['func'], col))

            context.SelectedColumns.append(aggrCol)

        # query = self.gdb.query(self.Model)
        query = self.gdb.query(*context.SelectedColumns)
        criterias = self._AddWheres(wheres, context)

        if criterias is not None:
            query = query.filter(criterias)

        for j in context.Joins:
            if j['type'] == 'inner':
                query = query.join(j['join'])
            elif j['type'] == 'outer':
                query = query.outerjoin(j['join'])

        if len(context.OrWheres) > 0:
            query = query.filter(or_(*context.OrWheres))

        if groupBy is not None:
            gb_col = self.GetFinalColumn(self.Model, groupBy, context)
            if gb_col is None:
                raise InvalidColumn(groupBy)

            query = query.group_by(gb_col)

        # print("{}".format("~" * 25))
        # print("dbHelper: Aggregate\r\n{}".format(str(query.statement.compile(compile_kwargs={"literal_binds": True}))))
        # print("{}".format("~" * 25))

        data = query.all()
        rows = data
        if not linear:
            rows = CgDbHelper._MakeDict(resultColumns, data)

        return (resultColumns, rows,)

    def getSingle(self, oid, serialize=True):
        if oid is None:
            return None

        query = self.gdb.query(self.Model)

        col = getattr(self.Model, self.PrimaryKey)
        query = query.filter((col == oid))

        col = getattr(self.Model, 'is_deleted', None)
        if col is not None:
            query = query.filter(col.is_(False))

        data = query.one_or_none()
        if data is None:
            return None

        if serialize:
            return data.serializeRoot()
        else:
            return data

    def getSingle2(self, oid, columns=[]):
        if oid is None:
            return None

        wheres = {
            'column': self.PrimaryKey,
            'search': oid
        }

        columns, data, total = self.getList(columns=columns, wheres=wheres, skipDelCheck=True, noCount=True)

        if len(data) > 0:
            return data[0]
        else:
            return None

    def getSingleForColumns(self, oid, columns=[]):
        if oid is None:
            return None

        cols = [c['colKey'] for c in columns]
        data = self.getSingle2(oid, cols)

        if data is None:
            return None

        if len(columns) > 0:
            record = {}
            for col in columns:
                if col['colKey'] in data:
                    record[col['colKey']] = data[col['colKey']]
                    if 'foreign_table' in col and data[col['colKey']] is not None:
                        model = CgDbHelper(self.gdb, self.Project, col['foreign_table'])

                        sub_record = model.getSingle2(data[col['colKey']], col['foreign_columns'])
                        sub_record.update({'id': sub_record[model.PrimaryKey]})
                        record['{}_data'.format(col['colKey'])] = [sub_record]
        else:
            record = data

        return record

    def insertRecord(self, data):
        if data is None:
            return None

        modelObj = self.Model()

        for k, v in data.items():
            if isinstance(v, str) and v == '':
                v = None

            attr = getattr(self.Model, k, None)
            if attr is not None:
                if 'hybrid_property' in attr.__class__.__name__:
                    continue
                # if hasattr(modelObj, k):
                setattr(modelObj, k, v)

        self.gdb.add(modelObj)
        self.gdb.flush()

        rowId = getattr(modelObj, self.PrimaryKey)
        return rowId

    def updateRecord(self, data):
        if data is None:
            return None

        row_id = data[self.PrimaryKey]
        modelObj = self.getSingle(row_id, serialize=False)

        if modelObj is None:
            raise RecordNotFound('updateRecord', '__id__|{}'.format(self.PrimaryKey), row_id)

        for k, v in data.items():
            if k == self.PrimaryKey:
                continue

            if isinstance(v, str) and v == '':
                v = None

            attr = getattr(self.Model, k, None)
            if attr is not None:
                if 'hybrid_property' in attr.__class__.__name__:
                    continue
                # if hasattr(modelObj, k):
                setattr(modelObj, k, v)

        return row_id

    def deleteRecord(self, oids):
        if not isinstance(oids, list):
            oids = [oids]

        for oid in oids:
            modelObj = self.getSingle(oid, False)
            if modelObj is None:
                print('Delete, record not found')
                continue

            col = getattr(self.Model, 'is_deleted', None)
            if col is not None:
                modelObj.is_deleted = True
            else:
                self.gdb.delete(modelObj)

        return

    def getFilterOptions(self, column, wheres=[]):
        _column = None

        allColumns = self.Model.__table__.columns._data.keys()
        allRelations = self.Model.__mapper__.relationships._data.keys()

        origCol = column
        if '.' in column:
            cols = column.split('.')
            if len(cols) > 2:
                raise InvalidColumn(column)

            column = cols[0]

        if column in allColumns:
            _column = getattr(self.Model, column, None)
            if _column is None:
                raise TableColumnNotFound(origCol)
        elif column in allRelations:
            if '.' not in origCol:
                raise InvalidColumn(origCol)

            Class = self.Model.__mapper__.relationships._data[column].mapper.class_
            if Class is None:
                raise TableColumnNotFound(origCol)

            _column = getattr(Class, cols[1])
        else:
            raise TableColumnNotFound(origCol)

        query = self.gdb.query(_column)

        for wh in wheres:
            column = wh['column']
            localWheres = []

            for search in wh['search']:
                localWheres.append((_column == search))

            if len(localWheres) > 0:
                query = query.filter(or_(*localWheres))

        query = query.order_by(_column)
        query = query.distinct(_column)

        data = query.all()
        data = [{'value': obj[0]} for obj in data]

        return data

    def CheckColumns(self, columns, context):
        allRelations = self.Model.__mapper__.relationships._data.keys()

        for col in columns:
            if col in allRelations and '.' not in col:
                raise InvalidColumn(col)

            column = self.GetFinalColumn(self.Model, col, context)
            if column is None:
                raise InvalidColumn(col)

            if context.SearchKey is not None:
                context.OrWheres.append(column.like("%%%s%%" % context.SearchKey))

            context.SelectedColumns.append(column)
        return

    def _AddWheres(self, where, context):
        whType = 'none'
        if 'group' in where and where['group'] is not None:
            whType = where['group'].lower()

        if whType == 'none':
            return self._MakeCriteria(where, context)

        _whereGroup = []
        for ch in where['children']:
            criteria = self._AddWheres(ch, context)
            if criteria is not None:
                _whereGroup.append(criteria)

        if whType == 'or':
            return or_(*_whereGroup)
        if whType == 'and':
            return and_(*_whereGroup)

        return None

    def _MakeCriteria(self, where, context):
        if 'column' not in where:
            return None

        _column = self.GetFinalColumn(self.Model, where['column'], context)

        if _column is None:
            raise InvalidColumn(where['column'])
            return None

        operator = where['op'].lower() if 'op' in where else 'eq'

        if operator == 'eq':
            return CgDbHelper._MakeCriteria_Eq(_column, where['search'])
        if operator == 'ne':
            return CgDbHelper._MakeCriteria_Ne(_column, where['search'])
        if operator == 'lt':
            return CgDbHelper._MakeCriteria_Lt(_column, where['search'])
        if operator == 'le':
            return CgDbHelper._MakeCriteria_Le(_column, where['search'])
        if operator == 'gt':
            return CgDbHelper._MakeCriteria_Gt(_column, where['search'])
        if operator == 'ge':
            return CgDbHelper._MakeCriteria_Ge(_column, where['search'])
        if operator == 'like':
            return CgDbHelper._MakeCriteria_Like(_column, where['search'])
        if operator == 'bt':
            return CgDbHelper._MakeCriteria_Between(_column, where['search'])

        return None

    def GetFinalColumn(self, model, column, context):
        cols = column.split('.')

        _column = getattr(model, cols[0], None)

        if _column is None:
            return None

        if len(cols) > 1:
            insp = _column.property.local_columns
            column = '.'.join(cols[1:])
            alias = None

            if cols[0] not in context.JoinRefs:
                alias = aliased(_column.mapper.class_)
                ln = {'join': (alias, _column)}

                if tuple(enumerate(insp))[0][1].nullable:
                    ln['type'] = 'outer'
                else:
                    ln['type'] = 'inner'

                context.Joins.append(ln)
                context.JoinRefs[cols[0]] = {'alias': alias, 'column': _column}

            else:
                alias = context.JoinRefs[cols[0]]['alias']

            return self.GetFinalColumn(alias, column, context)
        else:
            clsName = str(_column)
            if 'AliasedClass' in clsName:
                return _column.label('{}.{}'.format(model.__table__, cols[0]))
                # return aliased(_column)

            return _column

    @staticmethod
    def _MakeCriteria_Eq(_column, search):
        if not isinstance(search, list):
            return (_column == search)

        if len(search) == 1:
            return (_column == search[0])

        return _column.in_(search)

    @staticmethod
    def _MakeCriteria_Ne(_column, search):
        if not isinstance(search, list):
            return (_column != search)

        if len(search) == 1:
            return (_column != search[0])

        return _column.notin_(search)

    @staticmethod
    def _MakeCriteria_Lt(_column, search):
        if not isinstance(search, list):
            return (_column < search)

        if len(search) == 1:
            return (_column < search[0])

        _group = []

        for s in search:
            _group.append((_column < s))

        return or_(*_group)

    @staticmethod
    def _MakeCriteria_Le(_column, search):
        if not isinstance(search, list):
            return (_column <= search)

        if len(search) == 1:
            return (_column <= search[0])

        _group = []

        for s in search:
            _group.append((_column <= s))

        return or_(*_group)

    @staticmethod
    def _MakeCriteria_Gt(_column, search):
        if not isinstance(search, list):
            return (_column > search)

        if len(search) == 1:
            return (_column > search[0])

        _group = []

        for s in search:
            _group.append((_column > s))

        return or_(*_group)

    @staticmethod
    def _MakeCriteria_Ge(_column, search):
        if not isinstance(search, list):
            return (_column >= search)

        if len(search) == 1:
            return (_column >= search[0])

        _group = []

        for s in search:
            _group.append((_column >= s))

        return or_(*_group)

    @staticmethod
    def _MakeCriteria_Like(_column, search):
        if not isinstance(search, list):
            return (_column.like("%%%s%%" % search))

        if len(search) == 1:
            return (_column.like("%%%s%%" % search[0]))

        _group = []

        for s in search:
            _group.append((_column.like("%%%s%%" % s)))

        return or_(*_group)

    @staticmethod
    def _MakeCriteria_Between(_column, search):
        return (_column.between(search[0], search[1]))

    @staticmethod
    def _GetFirstColumn(model, column):
        cols = column.split('.')
        _column = getattr(model, cols[0], None)

        return _column

    @staticmethod
    def _GetValue(val):
        if hasattr(val, '_toJson'):
            return val._toJson()

        if isinstance(val, Decimal):
            return float(val)

        return val

    @staticmethod
    def _MakeDict(columns, data):
        data2 = []
        nColumns = len(columns)

        try:
            for row in data:
                r = {columns[i]: CgDbHelper._GetValue(row[i]) for i in range(0, nColumns)}
                data2.append(r)
        except IndexError:
            pass
            traceback.print_exc()

        return data2
