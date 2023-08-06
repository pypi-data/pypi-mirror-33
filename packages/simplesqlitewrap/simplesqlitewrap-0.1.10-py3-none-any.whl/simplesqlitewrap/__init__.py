import os
import sqlite3
from collections import namedtuple
from contextlib import contextmanager
from pprint import pformat


class Row:
    def __init__(self, column_names, column_values):
        for (cname, value) in zip(column_names, column_values):
            self.__dict__[cname] = value

    def __repr__(self):
        # return json.dumps({k: v for k, v in self.__dict__.items() if not isinstance(v, datetime.datetime)}, indent=4)
        return pformat(self.__dict__)


class Database:
    def __init__(self, file_path, connection_args=None):
        self._file_path = os.path.abspath(os.path.normpath(file_path))
        self._connection_args = connection_args

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self._file_path)
        yield conn
        conn.commit()
        conn.close()

    def _execute(
            self,
            statement,
            params=(),
            many=False,
            fetchall=False,
            fetchone=False,
            fetchfirst=False,
            rowcount=False,
            as_dict=False,
            as_obj=False,
            as_namedtuple=False,
            force_lowercase=False,
            **kwargs
    ):
        """
        Executes a SQL query.
        If 'fetchfirst' or 'rowcount' are passed, 'as_*' parameters will be ignored.
        If more than one 'as_*' parameter is passed, only the one with higher priority will be considered \
        (priority: as_dict > as_obj > as_namedtuple).

        :param statement: the SQL query to execute
        :param params: tuple of query params (list of tuples if many=True)
        :param many: if executemany() should be used instead of execute()
        :param fetchall: makes it return cursor.fetchall()
        :param fetchone: makes it return cursor.fetchone()
        :param fetchfirst: makes it return the first column of cursor.fetchone()
        :param rowcount: makes it return cursor.fetchone()
        :param as_dict: returns a list of dicts (or a dict if fetchone=True)
        :param as_obj: returns a list of Row classes (or a single class if fetchone=True)
        :param as_namedtuple: returns a list of named tuples (or a named tuple if fetchone=True)
        :param force_lowercase: if True and the result is returned as dict/class/namedtuple, keys/attr will be lowercase
        :return: None by default, or the requested result
        """
        # if [as_dict, as_obj, as_namedtuple].count(True) > 1:
            # raise ValueError("only one of 'as_dict', 'as_obj', 'as_namedtuple' must be True")
        # elif to_return_count == 1 and (rowcount or fetchfirst):
            # raise ValueError("'fetchfirst' and 'rowcount' can't be used in combination with 'as_*' parameters")


        result = None
        with self._conn() as conn:
            cursor = conn.cursor()

            if many:
                cursor.executemany(statement, params)
            else:
                cursor.execute(statement, params)

            if fetchall:
                result = cursor.fetchall()
            elif fetchone:
                result = cursor.fetchone()
            elif rowcount:
                result = cursor.rowcount
            elif fetchfirst:  # returns just the first column of the first row
                row = cursor.fetchone()
                if row:
                    result = row[0]

            if result and (as_dict or as_obj or as_namedtuple) and not (rowcount or fetchfirst):
                columns = [column[0].lower() if force_lowercase else column[0] for column in cursor.description]
                if as_dict:
                    return self._to_dict(columns, result)
                elif as_obj:
                    return self._to_obj(columns, result)
                elif as_namedtuple:
                    return self._to_namedtuples(columns, result)

        return result

    @staticmethod
    def _to_dict(columns, result):
        if isinstance(result, list):
            return [dict(zip(columns, row)) for row in result]
        else:  # tuple
            return dict(zip(columns, result))

    @staticmethod
    def _to_obj(columns, result):
        if isinstance(result, list):
            return [Row(columns, row) for row in result]
        else:  # tuple
            return Row(columns, result)

    @staticmethod
    def _to_namedtuples(columns, result):
        RowTuple = namedtuple('RowTuple', columns)
        if isinstance(result, list):
            return map(RowTuple._make, result)
        else:  # tuple
            return RowTuple._make(result)

    def __repr__(self):
        return 'sqlite3 database at {}'.format(self._file_path)
