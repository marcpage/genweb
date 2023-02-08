#!/usr/bin/env python3


import tempfile
import os
import threading
import queue

import genweb.database
from genweb.database import Join


RECORDS_TO_CREATE = 1000
THREADS_TO_TEST = 50


def add_items(db, table, in_queue, out_queue):
    while True:
        try:
            work = in_queue.get(timeout=0.100)
            db.insert(table, **work)

        except queue.Empty:
            break

    out_queue.put(db.get_all(table))


def test_Threadsafe():
    with tempfile.TemporaryDirectory() as workspace:
        db_path = os.path.join(workspace, "test.sqlite3")
        db = genweb.database.Connection.connect(f"sqlite://{db_path}?threadsafe=true")
        db.create_table("user",
            id="INTEGER PRIMARY KEY",
            name="VARCHAR(50)",
            email="VARCHAR(50)",
            password_hash="VARCHAR(64)",
            sponsor_id="INTEGER")
        user_queue = queue.Queue()
        users_queue = queue.Queue()
        threads = [threading.Thread(target=add_items,
                                    args=(db, 'user', user_queue, users_queue),
                                    daemon=True)
                    for _ in range(0, THREADS_TO_TEST)]

        for thread in threads:
            thread.start()

        for i in range(0, RECORDS_TO_CREATE):
            user_queue.put({
                'name': f"user #{i}",
                'email': f"user{i}@company.org",
                'password_hash': "3bce676cf7e5489dd539b077eb38888a1c9d42b23f88bc5c1f2af863f14ab23c"})

        for thread in threads:
            thread.join()

        iterations = 0

        while True:
            try:
                results = users_queue.get(timeout=0.100)
                assert len(results) == RECORDS_TO_CREATE
                assert len(set(u.email for u in results)) == RECORDS_TO_CREATE
                iterations += 1

            except queue.Empty:
                break

        assert iterations == THREADS_TO_TEST
        db.close()


def test_Sqlite():
    with tempfile.TemporaryDirectory() as workspace:
        db_path = os.path.join(workspace, "test.sqlite3")
        db = genweb.database.Connection.connect(f"sqlite://{db_path}?threadsafe=false")
        db.create_table("user",
            id="INTEGER PRIMARY KEY",
            name="VARCHAR(50)",
            email="VARCHAR(50)",
            password_hash="VARCHAR(64)",
            sponsor_id="INTEGER")

        john = db.insert('user',
            name="John",
            email="john.appleseed@apple.com",
            password_hash="3bce676cf7e5489dd539b077eb38888a1c9d42b23f88bc5c1f2af863f14ab23c",
            sponsor_id=None)
        assert john.id is not None
        assert john.name == "John"
        assert john.email == "john.appleseed@apple.com"
        assert john.password_hash == "3bce676cf7e5489dd539b077eb38888a1c9d42b23f88bc5c1f2af863f14ab23c"
        assert john.sponsor_id == None

        jane = db.insert('user',
            name="Jane",
            email="Jane.Doe@apple.com",
            password_hash="624fa374a759deff04da9e9d99b7e7f9937d9410401c421c38ca78973b98293a",
            sponsor_id=john.id)
        assert jane.id is not None
        assert jane.name == "Jane"
        assert jane.email == "Jane.Doe@apple.com"
        assert jane.password_hash == "624fa374a759deff04da9e9d99b7e7f9937d9410401c421c38ca78973b98293a"
        assert jane.sponsor_id == john.id

        everything = db.get_all('user')
        assert len(everything) == 2, everything

        db.close()

        db = genweb.database.Connection.connect(f"sqlite://{db_path}?threadsafe=false")
        db.create_table("user",
            id="INTEGER PRIMARY KEY",
            name="VARCHAR(50)",
            email="VARCHAR(50)",
            password_hash="VARCHAR(64)",
            sponsor_id="INTEGER")

        everything = db.get_all('user')
        assert len(everything) == 2, everything
        john = db.get_one_or_none('user', email="John.Appleseed@Apple.com", _where_="email LIKE :email")
        assert john.id is not None
        assert john.name == "John"
        assert john.email == "john.appleseed@apple.com"
        assert john.password_hash == "3bce676cf7e5489dd539b077eb38888a1c9d42b23f88bc5c1f2af863f14ab23c"
        assert john.sponsor_id == None

        jane = db.get_one_or_none('user', email="jane.doe@apple.com", _where_="email LIKE :email")
        assert jane.id is not None
        assert jane.name == "Jane", jane
        assert jane.email == "Jane.Doe@apple.com"
        assert jane.password_hash == "624fa374a759deff04da9e9d99b7e7f9937d9410401c421c38ca78973b98293a"
        assert jane.sponsor_id == john.id

        db.delete('user', 'id = :id', id=jane.id)
        no_jane = db.get_one_or_none('user', email="jane.doe@apple.com", _where_="email LIKE :email")
        assert no_jane is None, no_jane


def test_create_tables():
    with tempfile.TemporaryDirectory() as workspace:
        db_path = os.path.join(workspace, "test.sqlite3")
        db = genweb.database.Connection.connect(f"sqlite://{db_path}?threadsafe=false")
        db.create_tables(
            user={
                "id": "INTEGER PRIMARY KEY",
                "name": "VARCHAR(50)",
                "email": "VARCHAR(50)",
                "password_hash": "VARCHAR(64)",
                "sponsor_id": "INTEGER"
            },
            account={
                "id": "INTEGER PRIMARY KEY",
                "name": "VARCHAR(50)",
                "url": "VARCHAR(1085)",
                "user_id": "INTEGER"
            })

        john = db.insert('user',
            name="John",
            email="john.appleseed@apple.com",
            password_hash="3bce676cf7e5489dd539b077eb38888a1c9d42b23f88bc5c1f2af863f14ab23c",
            sponsor_id=None)
        assert john.id is not None
        assert john.name == "John"
        assert john.email == "john.appleseed@apple.com"
        assert john.password_hash == "3bce676cf7e5489dd539b077eb38888a1c9d42b23f88bc5c1f2af863f14ab23c"
        assert john.sponsor_id == None

        jane = db.insert('user',
            name="Jane",
            email="Jane.Doe@apple.com",
            password_hash="624fa374a759deff04da9e9d99b7e7f9937d9410401c421c38ca78973b98293a",
            sponsor_id=john.id)
        assert jane.id is not None
        assert jane.name == "Jane"
        assert jane.email == "Jane.Doe@apple.com"
        assert jane.password_hash == "624fa374a759deff04da9e9d99b7e7f9937d9410401c421c38ca78973b98293a"
        assert jane.sponsor_id == john.id

        everything = db.get_all('user')
        assert len(everything) == 2, everything

        db.close()

        db = genweb.database.Connection.connect(f"sqlite://{db_path}?threadsafe=false")
        db.create_table("user",
            id="INTEGER PRIMARY KEY",
            name="VARCHAR(50)",
            email="VARCHAR(50)",
            password_hash="VARCHAR(64)",
            sponsor_id="INTEGER")

        everything = db.get_all('user')
        assert len(everything) == 2, everything
        john = db.get_one_or_none('user', email="John.Appleseed@Apple.com", _where_="email LIKE :email")
        assert john.id is not None
        assert john.name == "John"
        assert john.email == "john.appleseed@apple.com"
        assert john.password_hash == "3bce676cf7e5489dd539b077eb38888a1c9d42b23f88bc5c1f2af863f14ab23c"
        assert john.sponsor_id == None

        jane = db.get_one_or_none('user', email="jane.doe@apple.com", _where_="email LIKE :email")
        assert jane.id is not None
        assert jane.name == "Jane"
        assert jane.email == "Jane.Doe@apple.com"
        assert jane.password_hash == "624fa374a759deff04da9e9d99b7e7f9937d9410401c421c38ca78973b98293a"
        assert jane.sponsor_id == john.id

        db.delete('user', 'id = :id', id=jane.id)
        no_jane = db.get_one_or_none('user', email="jane.doe@apple.com", _where_="email LIKE :email")
        assert no_jane is None, no_jane


def test_as_objects():
    with tempfile.TemporaryDirectory() as workspace:
        db_path = os.path.join(workspace, "test.sqlite3")
        db = genweb.database.Connection.connect(f"sqlite://{db_path}?threadsafe=false")
        db.create_tables(
            user={
                "id": "INTEGER PRIMARY KEY",
                "name": "VARCHAR(50)",
                "email": "VARCHAR(50)",
                "password_hash": "VARCHAR(64)",
                "sponsor_id": "INTEGER"
            })

        john = db.insert('user',
            name="John",
            email="john.appleseed@apple.com",
            password_hash="3bce676cf7e5489dd539b077eb38888a1c9d42b23f88bc5c1f2af863f14ab23c",
            sponsor_id=None,
            _as_object_=False)
        assert isinstance(john, dict)
        john = db.get_one_or_none('user', email="john.appleseed@apple.com", _as_object_=False)
        assert isinstance(john, dict)
        people = db.get_all('user', _as_objects_=False)
        assert len(people) == 1
        assert isinstance(people[0], dict)


def test_as_objects_default_off():
    with tempfile.TemporaryDirectory() as workspace:
        db_path = os.path.join(workspace, "test.sqlite3")
        db = genweb.database.Connection.connect(f"sqlite://{db_path}?threadsafe=false", default_return_objects=False)
        db.create_tables(
            user={
                "id": "INTEGER PRIMARY KEY",
                "name": "VARCHAR(50)",
                "email": "VARCHAR(50)",
                "password_hash": "VARCHAR(64)",
                "sponsor_id": "INTEGER"
            })

        john = db.insert('user',
            name="John",
            email="john.appleseed@apple.com",
            password_hash="3bce676cf7e5489dd539b077eb38888a1c9d42b23f88bc5c1f2af863f14ab23c",
            sponsor_id=None,
            _as_object_=False)
        assert isinstance(john, dict)
        john = db.get_one_or_none('user', email="john.appleseed@apple.com")
        assert isinstance(john, dict)
        people = db.get_all('user')
        assert len(people) == 1
        assert isinstance(people[0], dict)


def test_join():
    with tempfile.TemporaryDirectory() as workspace:
        db_path = os.path.join(workspace, "test.sqlite3")
        db = genweb.database.Connection.connect(f"sqlite://{db_path}?threadsafe=false", default_return_objects=False)
        db.create_tables(
            bank={
                "id": "INTEGER PRIMARY KEY",
                "name": "VARCHAR(50)",
            },
            account_type={
                'id': "INTEGER PRIMARY KEY",
                "name": "VARCHAR(50)",
                "bank_id": "INTEGER"
            })

        boa = db.insert('bank', name="Bank of America")
        boa_cc = db.insert('account_type', name='Customized Cash Rewards', bank_id=boa['id'])
        boa_check = db.insert('account_type', name='Advantage Banking', bank_id=boa['id'])

        chase = db.insert('bank', name="Chase")
        chase_cc = db.insert('account_type', name='Amazon Rewards', bank_id=chase['id'])
        chase_savings = db.insert('account_type', name='Chase Savings', bank_id=chase['id'])

        results = db.get_one_or_none('account_type', 'bank.id as bank_id', 'bank.name as bank_name', 'account_type.id as type_id', 'account_type.name as type_name',
                                    _join_ = Join('bank', 'bank.id = account_type.bank_id'),
                                    _where_="account_type.name = :type_name",
                                    type_name="Amazon Rewards")
        assert results['bank_id'] == chase['id']
        assert results['bank_name'] == chase['name']
        assert results['type_id'] == chase_cc['id']
        assert results['type_name'] == chase_cc['name']

        results = db.get_all('account_type', 'bank.id as bank_id', 'bank.name as bank_name', 'account_type.id as type_id', 'account_type.name as type_name',
                                    _join_ = Join('bank', 'bank.id = account_type.bank_id'))

        r_boa_cc = [t for t in results if t['type_name'] == "Customized Cash Rewards"][0]
        assert r_boa_cc['bank_id'] == boa['id']
        assert r_boa_cc['bank_name'] == boa['name']
        assert r_boa_cc['type_id'] == boa_cc['id']
        assert r_boa_cc['type_name'] == boa_cc['name']

        r_boa_check = [t for t in results if t['type_name'] == "Advantage Banking"][0]
        assert r_boa_check['bank_id'] == boa['id']
        assert r_boa_check['bank_name'] == boa['name']
        assert r_boa_check['type_id'] == boa_check['id']
        assert r_boa_check['type_name'] == boa_check['name']

        r_chase_cc = [t for t in results if t['type_name'] == "Amazon Rewards"][0]
        assert r_chase_cc['bank_id'] == chase['id']
        assert r_chase_cc['bank_name'] == chase['name']
        assert r_chase_cc['type_id'] == chase_cc['id']
        assert r_chase_cc['type_name'] == chase_cc['name']

        r_chase_savings = [t for t in results if t['type_name'] == "Chase Savings"][0]
        assert r_chase_savings['bank_id'] == chase['id']
        assert r_chase_savings['bank_name'] == chase['name']
        assert r_chase_savings['type_id'] == chase_savings['id']
        assert r_chase_savings['type_name'] == chase_savings['name']


def test_change():
    with tempfile.TemporaryDirectory() as workspace:
        db_path = os.path.join(workspace, "test.sqlite3")
        db = genweb.database.Connection.connect(f"sqlite://{db_path}?threadsafe=false")
        db.create_tables(
            user={
                "id": "INTEGER PRIMARY KEY",
                "name": "VARCHAR(50)",
                "email": "VARCHAR(50)",
                "password_hash": "VARCHAR(64)",
                "sponsor_id": "INTEGER"
            })

        john = db.insert('user',
            name="John",
            email="john.appleseed@apple.com",
            password_hash="3bce676cf7e5489dd539b077eb38888a1c9d42b23f88bc5c1f2af863f14ab23c",
            sponsor_id=None)
        assert john.id is not None
        assert john.name == "John"
        assert john.email == "john.appleseed@apple.com"
        assert john.password_hash == "3bce676cf7e5489dd539b077eb38888a1c9d42b23f88bc5c1f2af863f14ab23c"
        assert john.sponsor_id == None

        jane = db.insert('user',
            name="Jane",
            email="Jane.Doe@apple.com",
            password_hash="624fa374a759deff04da9e9d99b7e7f9937d9410401c421c38ca78973b98293a",
            sponsor_id=john.id)
        assert jane.id is not None
        assert jane.name == "Jane"
        assert jane.email == "Jane.Doe@apple.com"
        assert jane.password_hash == "624fa374a759deff04da9e9d99b7e7f9937d9410401c421c38ca78973b98293a"
        assert jane.sponsor_id == john.id

        everything = db.get_all('user')
        assert len(everything) == 2, everything

        db.close()

        db = genweb.database.Connection.connect(f"sqlite://{db_path}?threadsafe=false")

        everything = db.get_all('user')
        assert len(everything) == 2, everything
        john = db.get_one_or_none('user', email="John.Appleseed@Apple.com", _where_="email LIKE :email")
        assert john.id is not None
        assert john.name == "John"
        assert john.email == "john.appleseed@apple.com"
        assert john.password_hash == "3bce676cf7e5489dd539b077eb38888a1c9d42b23f88bc5c1f2af863f14ab23c"
        assert john.sponsor_id == None

        jane = db.get_one_or_none('user', email="jane.doe@apple.com", _where_="email LIKE :email")
        assert jane.id is not None
        assert jane.name == "Jane"
        assert jane.email == "Jane.Doe@apple.com"
        assert jane.password_hash == "624fa374a759deff04da9e9d99b7e7f9937d9410401c421c38ca78973b98293a"
        assert jane.sponsor_id == john.id

        db.change('user', 'user_id', _where_="id = :user_id", user_id=jane.id, email="jane.doe@apple.com")

        jane = db.get_one_or_none('user', email="jane.doe@apple.com", _where_="email LIKE :email")
        assert jane.id is not None
        assert jane.name == "Jane"
        assert jane.email == "jane.doe@apple.com"
        assert jane.password_hash == "624fa374a759deff04da9e9d99b7e7f9937d9410401c421c38ca78973b98293a"
        assert jane.sponsor_id == john.id

        db.close()

        db = genweb.database.Connection.connect(f"sqlite://{db_path}?threadsafe=false")

        jane = db.get_one_or_none('user', email="jane.doe@apple.com", _where_="email LIKE :email")
        assert jane.id is not None
        assert jane.name == "Jane"
        assert jane.email == "jane.doe@apple.com"
        assert jane.password_hash == "624fa374a759deff04da9e9d99b7e7f9937d9410401c421c38ca78973b98293a"
        assert jane.sponsor_id == john.id

        db.close()


if __name__ == "__main__":
    test_join()
    test_Sqlite()
    test_Threadsafe()
    test_create_tables()
    test_as_objects()
    test_as_objects_default_off()
    test_change()
