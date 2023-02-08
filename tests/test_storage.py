#!/usr/bin/env python3


import tempfile

from genweb import storage


def test_connect():
    with tempfile.TemporaryDirectory() as workspace:
        db_url = "sqlite:///" + workspace + "test.sqlite3"
        db = storage.connect(db_url)
        db.close()


if __name__ == "__main__":
    test_connect()
