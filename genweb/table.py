#!/usr/bin/env python3

""" Structure for models based on database
"""


import datetime


class DatabaseType:
    """Base class for all database types"""

    def __init__(self, allow_null: bool):
        self.allow_null = allow_null

    def null_clause(self):
        """Get the NOT NULL clause"""
        return "" if self.allow_null else " NOT NULL"

    def normalize(self, value):
        """convert value to usable type"""
        return value

    def denormalize(self, value):
        """convert usable type to database value"""
        return value


class Integer(DatabaseType):
    """integer"""

    def __init__(self, allow_null: bool = True):
        super().__init__(allow_null)

    def __str__(self):
        return f"INTEGER{self.null_clause()}"


class Fixed(Integer):
    """Fixed precision number"""

    def __init__(self, precision: int, allow_null: bool = True):
        self.__precision = precision
        super().__init__(allow_null)

    def normalize(self, value):
        """convert value (100) to usable type (10.00)"""
        return float(value) / pow(10, self.__precision)

    def denormalize(self, value):
        """convert usable type (10.00) to database value (100)"""
        return int(round(value * pow(10, self.__precision)))


class Money(Fixed):
    """Currency"""

    def __init__(self, precision: int = 2, allow_null: bool = True):
        super().__init__(precision, allow_null)


class Identifier(DatabaseType):
    """key"""

    def __init__(self):
        super().__init__(allow_null=False)

    def __str__(self):
        return f"INTEGER PRIMARY KEY{self.null_clause()}"


class ForeignKey(Integer):
    """key in another table"""

    def __init__(self, table, field_name: str = "id", allow_null: bool = True):
        super().__init__(allow_null)
        self.table = table
        self.field = field_name


class String(DatabaseType):
    """varchar"""

    def __init__(self, length, allow_null: bool = True):
        self.length = length
        super().__init__(allow_null)

    def __str__(self):
        return f"VARCHAR({self.length}){self.null_clause()}"


class Enum(String):
    """enum"""

    def __init__(self, enum_type, allow_null: bool = True):
        self.enum_type = enum_type
        largest = max(len(e.name) for e in list(enum_type))
        super().__init__(length=largest, allow_null=allow_null)

    def normalize(self, value):
        """convert string to enum"""
        return None if value is None else self.enum_type[value]

    def denormalize(self, value):
        """convert enum to string"""
        return None if value is None else value.name


class IntEnum(Integer):
    """enum"""

    def __init__(self, enum_type, allow_null: bool = True):
        self.enum_type = enum_type
        super().__init__(allow_null=allow_null)

    def normalize(self, value):
        """convert string to enum"""
        return None if value is None else self.enum_type(value)

    def denormalize(self, value):
        """convert enum to string"""
        return None if value is None else value.value


class Date(String):
    """Date or really VARCHAR"""

    def __init__(self, allow_null: bool = True):
        super().__init__(10, allow_null)

    def normalize(self, value):
        """convert value (YYYY-MM-DD HH:MM:SS.SSS) to usable type"""
        return (
            None
            if value is None
            else datetime.datetime.strptime(value.split(" ")[0], "%Y-%m-%d").date()
        )

    def denormalize(self, value):
        """convert usable type to database value (YYYY-MM-DD HH:MM:SS.SSS)"""
        return value.strftime("%Y-%m-%d") + " 00:00:00.000"


class IntDate(Integer):
    """Date as days since epoch"""

    ONE_DAY_IN_SECONDS = 60.0 * 60.0 * 24.0

    def normalize(self, value):
        """convert value (YYYY-MM-DD HH:MM:SS.SSS) to usable type"""
        return (
            None
            if value is None
            else datetime.datetime.fromtimestamp(
                value * IntDate.ONE_DAY_IN_SECONDS
            ).date()
        )

    def denormalize(self, value):
        """convert usable type to database value (YYYY-MM-DD HH:MM:SS.SSS)"""
        return int(
            datetime.datetime.combine(value, datetime.datetime.min.time()).timestamp()
            / IntDate.ONE_DAY_IN_SECONDS
        )


class Table:
    """Table model"""

    __IGNORE_TYPES = ["function", "staticmethod"]

    @staticmethod
    def name(table_subclass: type) -> str:
        """Get the name of a table from the type"""
        return table_subclass.__dict__.get("__table__", table_subclass.__name__)

    @staticmethod
    def database_description(*tables):
        """Get a description that can be passed to database"""
        return {
            Table.name(t): {f: Table.__describe(t, f) for f in Table.__fields(t)}
            for t in tables
        }

    @staticmethod
    def __is_field(name: str, table_subclass: type) -> bool:
        maybe = not name.startswith("_") and name in table_subclass.__dict__
        return (
            maybe
            and table_subclass.__dict__[name].__class__.__name__
            not in Table.__IGNORE_TYPES
        )

    @staticmethod
    def __describe(table_subclass: type, field: str) -> str:
        return str(Table.__type(table_subclass, field))

    @staticmethod
    def __type(table_subclass: type, field: str) -> DatabaseType:
        return table_subclass.__dict__[field]

    @staticmethod
    def __fields(table_subclass: type) -> [str]:
        return [f for f in dir(table_subclass) if Table.__is_field(f, table_subclass)]

    @staticmethod
    def normalize_field(table_subclass: type, field: str, value: any) -> any:
        """Convert a field from database format to usable format"""
        return Table.__type(table_subclass, field).normalize(value)

    @staticmethod
    def denormalize_field(table_subclass: type, field: str, value: any) -> any:
        """convert a field from usable format to database format"""
        return Table.__type(table_subclass, field).denormalize(value)

    def __init_subclass__(cls: type):
        super().__init_subclass__()
        fields = [f for f in dir(cls) if Table.__is_field(f, cls)]
        assert fields, f"No fields in {cls.__name__}"

    def __repr__(self):
        fields = Table.__fields(self.__class__)
        parameters = ", ".join(
            f"{f}={repr(self.__dict__.get(f, None))}" for f in fields
        )
        return f"{self.__class__.__name__}({parameters})"

    def __str__(self):
        fields = Table.__fields(self.__class__)
        parameters = ", ".join(f"{f}={str(self.__dict__[f])}" for f in fields)
        return f"{Table.name(self.__class__)}({parameters})"

    def __init__(self, **kwargs):
        do_normalize = kwargs.get("_normalize_", True)

        if "_normalize_" in kwargs:
            del kwargs["_normalize_"]

        self.__dict__ = kwargs

        if do_normalize:
            self.normalize()

    def normalize(self):
        """Converts database types to user-friendly types"""
        for field in Table.__fields(self.__class__):
            denormalized = self.__dict__.get(field, None)
            normalized = Table.normalize_field(self.__class__, field, denormalized)
            self.__dict__[field] = normalized

    def denormalize(self) -> dict:
        """Converts usable types to database types"""
        return {
            f: Table.denormalize_field(self.__class__, f, self.__dict__.get(f, None))
            for f in Table.__fields(self.__class__)
        }
