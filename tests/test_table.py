#!/usr/bin/env python3


import datetime
import enum


from genweb.table import Table, Integer, Identifier, String, Date, Fixed, IntEnum, Enum, Money, ForeignKey, IntDate


def test_basic():
    class User(Table):
        id = Identifier()
        name = String(50)
        count = Integer()

    user = User(a=5,name="John")
    assert user.id is None
    assert user.name == "John"
    assert user.count is None, f"user.count = {user.count}"
    assert repr(user).startswith("User(")
    assert str(user).startswith("User(")
    description = Table.database_description(User)
    assert 'PRIMARY KEY' in description['User']['id'], description
    assert 'INTEGER' == description['User']['count'], description
    assert 'VARCHAR(50)' == description['User']['name'], description


def test_table_name():
    class User(Table):
        __table__='user'
        id = Identifier()
        name = String(50)

    user = User(a=5,name="Jane")
    assert user.id is None
    assert user.name == "Jane"
    description = Table.database_description(User)
    assert 'user' in description, description
    assert repr(user).startswith("User(")
    assert str(user).startswith("user(")


def test_normalize():
    class User(Table):
        __table__='user'
        id = Identifier()
        name = String(50)
        def normalize(self):
            super().normalize()
            self.name = self.name.upper()
        def denormalize(self):
            value = super().denormalize()
            value['name'] = value['name'].lower()
            return value

    user = User(id=1, name="John")
    assert user.id == 1
    assert user.name == "JOHN"
    for_db = user.denormalize()
    assert for_db['name'] == 'john'


def test_date():
    class User(Table):
        id = Identifier()
        name = String(50)
        birthday = Date()
    user = User(name="John", birthday="1973-06-30 00:00:00.000")
    assert user.id is None
    assert user.name == "John"
    assert user.birthday == datetime.date(1973, 6, 30)
    assert user.denormalize()['birthday'] == "1973-06-30 00:00:00.000"


def test_integer_date():
    class User(Table):
        id = Identifier()
        name = String(50)
        birthday = IntDate()
    birthday_in_days = datetime.datetime(1973, 6, 30).timestamp()/24/60/60
    user = User(name="John", birthday=birthday_in_days)
    assert user.id is None
    assert user.name == "John"
    assert user.birthday == datetime.date(1973, 6, 30), f"{user.birthday} <> {datetime.date(1973, 6, 30)}"
    assert user.denormalize()['birthday'] == int(birthday_in_days), f"{user.denormalize()['birthday']} <> {birthday_in_days}"


def test_fixed():
    class User(Table):
        id = Identifier()
        name = String(50)
        balance = Fixed(2)
        rate = Fixed(2)
    user = User(name="John", balance=13544, rate=367)
    assert user.id is None
    assert user.name == "John"
    assert abs(user.balance - 135.44) < 0.001
    assert abs(user.rate - 3.67) < 0.001
    for_db = user.denormalize()
    assert for_db['balance'] == 13544
    assert for_db['rate'] == 367


def test_methods():
    class User(Table):
        id = Identifier()
        name = String(50)
        title = String(8)

        def address(self):
            return f"{self.title} {self.name}"

    user = User(id=1, name="John", title="Mr.")
    assert user.address() == "Mr. John"


def test_methods():
    class User(Table):
        id = Identifier()
        name = String(50)
        title = String(8)

        @staticmethod
        def table():
            return f"User"

    assert User.table() == "User"


def test_enums():
    class Colors(enum.Enum):
        BLUE = 1
        HAZEL = 2
        BROWN = 3
        GREEN = 4

    class User(Table):
        id = Identifier()
        name = String(50)
        eyecolor = Enum(Colors)

    user = User(id=1, name="John", eyecolor="HAZEL")
    assert user.eyecolor == Colors.HAZEL
    assert user.denormalize()['eyecolor'] == 'HAZEL'


def test_multiple_tables():
    class User(Table):
        id = Identifier()
        name = String(50)

    class Account(Table):
        __table__ = 'table'
        id = Identifier()
        name = String(50)

    description = Table.database_description(User, Account)
    assert 'table' in description
    assert 'User' in description


def test_money():
    class Account(Table):
        __table__ = 'table'
        id = Identifier()
        name = String(50)
        balance = Money()

    account = Account(id=1, name="John", balance=314)
    assert abs(account.balance - 3.14) < 0.001
    assert account.denormalize()['balance'] == 314

    account = Account(id=1, name="John", balance=313)
    assert abs(account.balance - 3.13) < 0.001
    assert account.denormalize()['balance'] == 313

    account = Account(id=1, name="John", balance=312)
    assert abs(account.balance - 3.12) < 0.001
    assert account.denormalize()['balance'] == 312

    account = Account(id=1, name="John", balance=311)
    assert abs(account.balance - 3.11) < 0.001
    assert account.denormalize()['balance'] == 311

    account = Account(id=1, name="John", balance=310)
    assert abs(account.balance - 3.10) < 0.001
    assert account.denormalize()['balance'] == 310

    account = Account(id=1, name="John", balance=315)
    assert abs(account.balance - 3.15) < 0.001
    assert account.denormalize()['balance'] == 315

    account = Account(id=1, name="John", balance=316)
    assert abs(account.balance - 3.16) < 0.001
    assert account.denormalize()['balance'] == 316

    account = Account(id=1, name="John", balance=317)
    assert abs(account.balance - 3.17) < 0.001
    assert account.denormalize()['balance'] == 317

    account = Account(id=1, name="John", balance=318)
    assert abs(account.balance - 3.18) < 0.001
    assert account.denormalize()['balance'] == 318

    account = Account(id=1, name="John", balance=319)
    assert abs(account.balance - 3.19) < 0.001
    assert account.denormalize()['balance'] == 319


def test_foreign_key():
    class User(Table):
        id = Identifier()
        name = String(50)

    class Account(Table):
        __table__ = 'table'
        id = Identifier()
        user_id = ForeignKey(User)
        name = String(50)
        balance = Money()

    user = User(id=1, name="John")
    account = Account(id=1, user_id=user.id, name="Savings", balance=314)
    assert account.user_id == user.id


def test_enum():
    class Eyecolor(enum.Enum):
        BROWN = 1
        BLUE = 2
        HAZEL = 3
        GREEN = 4

    class User(Table):
        id = Identifier()
        name = String(50)
        eyecolor = Enum(Eyecolor)

    user = User(id=1, name="john", eyecolor = 'HAZEL')
    assert user.eyecolor == Eyecolor.HAZEL
    assert user.denormalize()['eyecolor'] == 'HAZEL'
    description = Table.database_description(User)
    assert description['User']['eyecolor'] == 'VARCHAR(5)'


def test_init_normalize():
    class Eyecolor(enum.Enum):
        BROWN = 1
        BLUE = 2
        HAZEL = 3
        GREEN = 4

    class User(Table):
        id = Identifier()
        name = String(50)
        eyecolor = Enum(Eyecolor)

    user = User(id=1, name="john", eyecolor = Eyecolor.HAZEL, _normalize_=False)
    assert user.eyecolor == Eyecolor.HAZEL
    assert user.denormalize()['eyecolor'] == 'HAZEL'
    description = Table.database_description(User)
    assert description['User']['eyecolor'] == 'VARCHAR(5)'

    user = User(id=1, name="john", eyecolor = 'HAZEL', _normalize_=True)
    assert user.eyecolor == Eyecolor.HAZEL
    assert user.denormalize()['eyecolor'] == 'HAZEL'
    description = Table.database_description(User)
    assert description['User']['eyecolor'] == 'VARCHAR(5)'


def test_intenum():
    class Eyecolor(enum.Enum):
        BROWN = 1
        BLUE = 2
        HAZEL = 3
        GREEN = 4

    class User(Table):
        id = Identifier()
        name = String(50)
        eyecolor = IntEnum(Eyecolor)

    user = User(id=1, name="john", eyecolor = 3)
    assert user.eyecolor == Eyecolor.HAZEL
    assert user.denormalize()['eyecolor'] == 3
    description = Table.database_description(User)
    assert description['User']['eyecolor'] == 'INTEGER'


def test_more_methods():
    class User(Table):
        id = Identifier()
        name = String(50, allow_null=False)
        email = String(50, allow_null=False)
        password_hash = String(64, allow_null=False)
        sponsor_id = ForeignKey("User")
        @staticmethod
        def hash_password(text): pass
        @staticmethod
        def create(email: str, name: str, password: str, sponsor_id: int = None): pass
        @staticmethod
        def fetch(user_id: int): pass
        @staticmethod
        def lookup(email: str): pass
        @staticmethod
        def every(): pass
        @staticmethod
        def total(): pass
        def sponsored(self): pass
        def change(self, **_to_update_): pass

    description = Table.database_description(User)
    assert 'name' in description['User'], description
    assert 'id' in description['User'], description
    assert 'email' in description['User'], description
    assert 'password_hash' in description['User'], description
    assert 'sponsor_id' in description['User'], description
    assert 'hash_password' not in description['User'], description
    assert 'create' not in description['User'], description
    assert 'fetch' not in description['User'], description
    assert 'lookup' not in description['User'], description
    assert 'every' not in description['User'], description
    assert 'total' not in description['User'], description
    assert 'sponsored' not in description['User'], description
    assert 'change' not in description['User'], description


if __name__ == "__main__":
    test_basic()
    test_table_name()
    test_normalize()
    test_date()
    test_fixed()
    test_methods()
    test_enums()
    test_multiple_tables()
    test_money()
    test_enum()
    test_foreign_key()
    test_more_methods()
    test_integer_date()
    test_intenum()
    test_init_normalize()
