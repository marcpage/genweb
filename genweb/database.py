#!/usr/bin/env python3

""" Abstract the database API
"""


import sqlite3
import threading
import queue
import types
import urllib.parse
import enum


class JoinType(enum.Enum):
    """Types of join statements"""

    INNER = 1
    LEFT = 2
    RIGHT = 3
    FULL = 4


class Join:
    """Represents a join statement"""

    def __init__(self, table: str, criteria: dict, join_type=JoinType.INNER):
        self.table = table
        self.criteria = criteria
        self.method = join_type.name

    def __str__(self):
        return f" {self.method} JOIN {self.table} ON {self.criteria}"

    def __getitem__(self, item):
        return [self][item]


class Sqlite:
    """Basic kernel for sqlite3 database"""

    def __init__(self, description):
        self.__db = sqlite3.connect(description)
        self.__thread = threading.current_thread().ident

    def execute(
        self,
        statement: str,
        replacements: any = None,
        fetch_all: bool = None,
        commit: bool = False,
    ) -> (int, [str], list, int):
        """Executes an sqlite3 statement
        replacements - dictionary (:name -> dict['name']) or list (? -> [0])
        fetch_all - None= no values to return, False = fetch one or none
        commit - tell the database to commit after executing
        """
        assert (
            self.__thread == threading.current_thread().ident
        ), f"Thread mismatch {self.__thread} bs {threading.current_thread().ident}"
        cursor = self.__db.cursor()
        cursor.execute(statement, tuple() if replacements is None else replacements)

        if commit:
            self.__db.commit()

        if fetch_all is not None:
            results = cursor.fetchall() if fetch_all else cursor.fetchone()
        else:
            results = None

        labels = (
            [] if cursor.description is None else [c[0] for c in cursor.description]
        )
        return cursor.lastrowid, labels, results, cursor.rowcount

    def close(self):
        """Close the database"""
        self.__db.close()


class Threadsafe(threading.Thread):
    """Wrapper to make a database kernel threadsafe"""

    def __init__(self, description, db_type):
        self.__description = description
        self.__type = db_type
        self.__messages = queue.Queue()
        threading.Thread.__init__(self, daemon=True)
        self.start()

    def run(self):
        """handle the messages"""
        database = self.__type(self.__description)

        while True:
            message = self.__messages.get()

            if message is None:
                break

            message[1].put(database.execute(**message[0]))

        database.close()

    def execute(
        self,
        statement: str,
        replacements: tuple = None,
        fetch_all: bool = None,
        commit: bool = False,
    ) -> (int, [str], list):
        """Pass an sqlite3 statement to the execution thread
        replacements - dictionary (:name -> dict['name']) or list (? -> [0])
        fetch_all - None= no values to return, False = fetch one or none
        commit - tell the database to commit after executing
        """
        response = queue.Queue()
        self.__messages.put(
            (
                {
                    "statement": statement,
                    "replacements": replacements,
                    "fetch_all": fetch_all,
                    "commit": commit,
                },
                response,
            )
        )
        return response.get()

    def close(self):
        """pass the close message to the execution thread and wait for completion"""
        self.__messages.put(None)
        self.join()


class Connection:
    """A database connection"""

    ACCPEPTED_SCHEMES = ["sqlite"]

    @staticmethod
    def connect(url: str, default_return_objects=True):
        """Connect to a database
        url - sqlite://<path>?threadsafe=true
        """
        parts = urllib.parse.urlparse(url)
        assert parts.scheme in Connection.ACCPEPTED_SCHEMES, parts.scheme
        database = None

        if parts.scheme == "sqlite":
            query = urllib.parse.parse_qs(parts.query)

            if "false" in [v.lower() for v in query.get("threadsafe", [])]:
                database = Sqlite(parts.path)
            else:
                database = Threadsafe(parts.path, Sqlite)

        return Connection(database, default_return_objects)

    def __init__(self, database, default_return_objects=True):
        """Create the connection
        database - an instance of Sqlite or equivalent
        """
        self.__db = database
        self.default_return_objects = default_return_objects

    @staticmethod
    def __convert(description: [str], row: list, as_object: bool):
        if row is None:
            return None

        data = dict(zip(description, row))
        return types.SimpleNamespace(**data) if as_object else data

    def execute(
        self, sql_command: str, replacements: any, commit: bool = True
    ) -> (int, [str], list, int):
        """execute SQL command w/ the given replacements and optionally committing"""
        return self.__db.execute(sql_command, replacements, commit=commit)

    def fetch_one_or_none(self, _sql_command_: str, **_replacements_) -> any:
        """Return the first match or None if no matches
        _as_object_ - (True) If True return objects, False return dictionaries
        """
        as_object = _replacements_.get("_as_object_", self.default_return_objects)
        results = self.__db.execute(_sql_command_, _replacements_, fetch_all=False)
        return Connection.__convert(results[1], results[2], as_object)

    def fetch_all(self, _sql_command_: str, **_replacements_) -> [any]:
        """Return all results from the query
        _as_objects_ - (True) If True return objects, False return dictionaries
        """
        as_objects = _replacements_.get("_as_objects_", self.default_return_objects)
        results = self.__db.execute(_sql_command_, _replacements_, fetch_all=True)
        return [Connection.__convert(results[1], r, as_objects) for r in results[2]]

    def create_table(self, _table_name_: str, **_description_):
        """Create a table
        _table_name_ - the name of the table to create
        _description_ - pass in name of column mapped to SQL description
        _if_not_exists_ - (True) If True add the "IF NOT EXISTS" clause
        """
        if_not_exists = _description_.get("_if_not_exists_", True)
        description_string = ", ".join(f'"{n}" {v}' for n, v in _description_.items())
        exists_string = " IF NOT EXISTS" if if_not_exists else ""
        self.execute(
            f"""CREATE TABLE{exists_string} "{_table_name_}" ({description_string});""",
            {},
            commit=False,
        )

    def create_tables(self, **_description_):
        """Creates tables from descriptions.
        _description_ - keyword arguments of table={row:description}
        _if_not_exists_ - (True) If True add the "IF NOT EXISTS" clause
        """
        if_not_exists = _description_.get("_if_not_exists_", True)

        for table_name, table_description in _description_.items():
            self.create_table(
                table_name, **table_description, _if_not_exists_=if_not_exists
            )

    def insert(self, _table_name_: str, **_data_) -> any:
        """Insert a new row in the table
        _table_name_ - the table to insert data into
        _data_ - map of column name to data to put in the table
        _as_object_ - (True) If True return an object, False return a dictionary
        _commit_ - (True) should a commit be done after the operation
        """
        fields = ["_as_object_", "_commit_", "_id_name_"]
        as_object = _data_.get("_as_object_", self.default_return_objects)
        commit = _data_.get("_commit_", True)
        id_name = _data_.get("_id_name_", "id")
        columns = sorted(c for c in _data_ if c not in fields)
        placeholders = ", ".join("?" for _ in range(0, len(columns)))
        replacements = [_data_[c] for c in columns]
        column_string = ", ".join(f"{c}" for c in columns)
        results = self.execute(
            f"""INSERT INTO {_table_name_} ({column_string}) VALUES({placeholders});""",
            replacements,
            commit=commit,
        )
        assert results[3] > 0, "No rows were inserted {results}"

        if id_name is not None:
            _data_ = dict(_data_)
            _data_[id_name] = results[0]

        return types.SimpleNamespace(**_data_) if as_object else _data_

    def change(self, _table_name_, *_where_columns_, **_data_):
        """Insert a new row in the table
        _table_name_ - the table to insert data into
        _where_ - The WHERE clause
        _data_ - map of column name to data to update in the table
        _commit_ - (True) should a commit be done after the operation
        """
        assert _data_.get("_where_", None), "You must specify _where_"
        fields = ["_commit_", "_where_"]
        commit = _data_.get("_commit_", True)
        where = _data_.get("_where_", None)
        columns = sorted(
            c for c in _data_ if c not in fields and c not in _where_columns_
        )
        set_string = ", ".join(f"{n} = :arg{i}" for i, n in enumerate(columns))
        replacements = {f"arg{i}": _data_[c] for i, c in enumerate(columns)}
        replacements.update({c: _data_[c] for c in _where_columns_})
        results = self.execute(
            f"""UPDATE {_table_name_} SET {set_string} WHERE {where};""",
            replacements,
            commit=commit,
        )
        assert results[3] > 0, "No rows were changed {results}"

    def get_one_or_none(self, _table_name_: str, *_columns_, **_replacements_) -> any:
        """Get the first result or None if there are no results
        _table_name_ - The table to query
        _where_ - The WHERE clause
        _join_ - A Join object or list of Join objects
        _columns_ - list the names of any columns you want returned or none for all columns
        _replacements_ - :name in where will be replaced with name=value
        _as_object_ - (True) If True return an object, False return a dictionary
        """
        where = _replacements_.get("_where_", None)
        where_string = "" if not where else f" WHERE {where}"
        join_clause = _replacements_.get("_join_", [""])
        join_string = "".join(str(j) for j in join_clause)
        column_string = (
            "*" if len(_columns_) == 0 else ", ".join(f"{c}" for c in _columns_)
        )
        return self.fetch_one_or_none(
            f"""SELECT {column_string} FROM {_table_name_}{join_string}{where_string};""",
            **_replacements_,
        )

    def get_all(self, _table_name_: str, *_columns_, **_replacements_) -> [any]:
        """Get all the results that match
        _table_name_ - The table to query
        _where_ - The WHERE clause
        _join_ - A Join object or list of Join objects
        _columns_ - list the names of any columns you want returned or none for all columns
        _replacements_ - :name in where will be replaced with name=value
        _as_objects_ - (True) If True return objects, False return dictionaries
        """
        where = _replacements_.get("_where_", None)
        column_string = (
            "*" if len(_columns_) == 0 else ", ".join(f"{c}" for c in _columns_)
        )
        where_string = "" if where is None else f" WHERE {where}"
        join_clause = _replacements_.get("_join_", [""])
        join_string = "".join(str(j) for j in join_clause)
        return self.fetch_all(
            f"""SELECT {column_string} FROM {_table_name_}{join_string}{where_string};""",
            **_replacements_,
        )
        # group_by:list=None, order_clause=None
        # order_ascending=True, limit=None, offset=None

    def delete(self, _table_name_: str, _where_: str, **_replacements_) -> int:
        """delete a row from the table
        _table_name_ - the table to delete the row from
        _where_ - The where clause
        _replacements_ - :name in where will be replaced with name=value
        """
        commit = _replacements_.get("commit", True)
        results = self.execute(
            f"""DELETE FROM {_table_name_} WHERE {_where_}""",
            _replacements_,
            commit=commit,
        )
        return results[3]

    def close(self):
        """Close out the database"""
        self.__db.close()
