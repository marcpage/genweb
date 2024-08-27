#!/usr/bin/env python3


""" Test the V1 web api """


from json import loads, dumps
from types import SimpleNamespace
from io import BytesIO
from os.path import join, dirname

from genweb.webapi_v1 import ApiV1
import genweb.genweb
import genweb.webapi_v1


DATA_DIR = join(dirname(__file__), "data")


class MockHandler:
    def __init__(self, path):
        self.path = path
        self.headers = {}
        self.rfile = None

    def set_body(self, body: bytes):
        self.headers["Content-Length"] = len(body)
        self.rfile = BytesIO(body)
        return self


class MockMetadata(dict):
    def __init__(self, path=None, **fields):
        self.saved = False
        self.path = path
        super().__init__(fields)

    def save(self):
        self.saved = True


class MockSettings:
    def __init__(self, path: str):
        self.path = path
        self.dict = {
            "gedcom_path": None,
            "metadata_yaml": None,
            "binaries_dir": DATA_DIR,
            "alias_path": None,
        }
        super().__init__()

    def __getitem__(self, key: str) -> dict:
        return self.dict.__getitem__(key)

    def get(self, key, default):
        print(f"get({key}, {default})")
        return self.dict.get(key, default)


class MockPeople:
    def __init__(self, gedcom, aliaspath):
        self.gedcom = gedcom
        self.aliaspath = aliaspath


def test_list_people() -> None:
    api = ApiV1()
    api.settings = {}
    api.people = {"person1": None, "person2": None}
    api.metadata = MockMetadata()
    handler = MockHandler(ApiV1.URL + "people")
    body, mime, code = api.handle_get(handler)
    people = loads(body)
    assert set(people) == set(api.people.keys()), body
    assert mime == "text/json"
    assert code == 200
    assert not api.metadata.saved


def test_list_metadata() -> None:
    api = ApiV1()
    api.settings = {}
    api.people = {}
    api.metadata = MockMetadata(metadata1=None, metadata2=None)
    handler = MockHandler(ApiV1.URL + "metadata")
    body, mime, code = api.handle_get(handler)
    metadata = loads(body)
    assert set(metadata) == set(api.metadata.keys()), body
    assert mime == "text/json"
    assert code == 200
    assert not api.metadata.saved


def test_get_person() -> None:
    api = ApiV1()
    api.settings = {}
    api.people = {
        "person1": SimpleNamespace(
            given="John Albert",
            surname="Doe",
            birthdate=None,
            deathdate=None,
            gender="M",
            id="person1",
            spouses=[],
            children=[],
            parents=[],
            metadata=[],
        ),
        "person2": SimpleNamespace(),
    }
    api.metadata = MockMetadata()
    handler = MockHandler(ApiV1.URL + "people/person1")
    body, mime, code = api.handle_get(handler)
    person = loads(body)
    assert person["given"] == api.people["person1"].given, body
    assert person["surname"] == api.people["person1"].surname, body
    assert person["gender"] == api.people["person1"].gender, body
    assert mime == "text/json"
    assert code == 200
    assert not api.metadata.saved


def test_get_metadata() -> None:
    api = ApiV1()
    api.settings = {}
    api.people = {}
    api.metadata = MockMetadata(metadata1={"a": 1, "b": 2}, metadta2={"c": 3, "d": 4})
    handler = MockHandler(ApiV1.URL + "metadata/metadata1")
    body, mime, code = api.handle_get(handler)
    metadata = loads(body)
    assert metadata == api.metadata["metadata1"]
    assert mime == "text/json"
    assert code == 200
    assert not api.metadata.saved


def test_post_metadata() -> None:
    api = ApiV1()
    api.settings = {}
    api.people = {}
    api.metadata = MockMetadata()
    handler = MockHandler(ApiV1.URL + "metadata/metadata1")
    post_metadata = {
        "a": 1,
        "b": 2,
        "people": "a,b, c\r\nd\ne f;g:h",
        "c": "",
        "width": "50",
    }
    handler.set_body(dumps(post_metadata).encode("utf-8"))
    body, mime, code = api.handle_post(handler)
    metadata = loads(body)
    assert set(metadata) == set(post_metadata) - {"c"}, body
    assert metadata["a"] == post_metadata["a"], body
    assert metadata["b"] == post_metadata["b"], body
    assert "c" not in metadata, body
    assert set(metadata["people"]) == set("abcdefgh"), body
    assert metadata["width"] == 50, body
    assert mime == "text/json"
    assert code == 200
    assert api.metadata.saved


def test_non_api() -> None:
    api = ApiV1()
    api.settings = {}
    api.people = {}
    api.metadata = MockMetadata()
    handler = MockHandler(ApiV1.URL + "bogus")

    try:
        _, _, _ = api.handle_post(handler)
        raise AssertionError("Expected exception")

    except AssertionError:
        pass

    try:
        _, _, _ = api.handle_get(handler)
        raise AssertionError("Expected exception")

    except AssertionError:
        pass

    handler = MockHandler(ApiV1.URL + "bogus/identifier")

    try:
        _, _, _ = api.handle_post(handler)
        raise AssertionError("Expected exception")

    except AssertionError:
        pass

    try:
        _, _, _ = api.handle_get(handler)
        raise AssertionError("Expected exception")

    except AssertionError:
        pass

    handler = MockHandler(ApiV1.URL + "metadata/identifier/")

    try:
        _, _, _ = api.handle_post(handler)
        raise AssertionError("Expected exception")

    except AssertionError:
        pass

    try:
        _, _, _ = api.handle_get(handler)
        raise AssertionError("Expected exception")

    except AssertionError:
        pass

    handler = MockHandler(ApiV1.URL + "metadata/")

    try:
        _, _, _ = api.handle_post(handler)
        raise AssertionError("Expected exception")

    except AssertionError:
        pass

    try:
        _, _, _ = api.handle_get(handler)
        raise AssertionError("Expected exception")

    except AssertionError:
        pass

    handler = MockHandler(ApiV1.URL + "metadata/identifier/bogus")

    try:
        _, _, _ = api.handle_post(handler)
        raise AssertionError("Expected exception")

    except AssertionError:
        pass

    try:
        _, _, _ = api.handle_get(handler)
        raise AssertionError("Expected exception")

    except AssertionError:
        pass


def test_metadata_404() -> None:
    api = ApiV1()
    api.settings = {}
    api.people = {}
    api.metadata = MockMetadata(metadata1={"a": 1, "b": 2}, metadta2={"c": 3, "d": 4})
    handler = MockHandler(ApiV1.URL + "metadata/metadata5")
    body, mime, code = api.handle_get(handler)
    assert code == 404
    assert not api.metadata.saved


def test_person_404() -> None:
    api = ApiV1()
    api.settings = {}
    api.people = {"person1": SimpleNamespace(), "person2": SimpleNamespace()}
    api.metadata = MockMetadata()
    handler = MockHandler(ApiV1.URL + "people/person5")
    body, mime, code = api.handle_get(handler)
    assert code == 404
    assert not api.metadata.saved


def test_is_call() -> None:
    api = ApiV1()
    api.settings = {}
    api.people = {}
    api.metadata = MockMetadata()
    assert api.is_call(MockHandler(ApiV1.URL + "people"))
    assert api.is_call(MockHandler(ApiV1.URL + "metadata"))
    assert not api.is_call(MockHandler(ApiV1.URL + "bogus"))
    assert api.is_call(MockHandler(ApiV1.URL + "people/person1"))
    assert api.is_call(MockHandler(ApiV1.URL + "metadata/metadata1"))
    assert not api.is_call(MockHandler(ApiV1.URL + "bogus/bogus1"))
    assert not api.is_call(MockHandler(ApiV1.URL))
    assert not api.is_call(MockHandler(ApiV1.URL + "people/"))
    assert not api.is_call(MockHandler(ApiV1.URL + "metadata/"))
    assert not api.is_call(MockHandler(ApiV1.URL + "people/person1/"))
    assert not api.is_call(MockHandler(ApiV1.URL + "metadata/metadata1/"))


def test_load() -> None:
    genweb.genweb.PRINT = lambda _: None
    people = {
        "p1": SimpleNamespace(
            id="1",
            parents=[],
            given="John",
            surname="Doe",
            birthdate=None,
            deathdate=None,
            metadata=[],
            children=[],
            spouses=[],
        )
    }
    metadata = {"m1": {"people": ["p1", "p2"]}, "m2": {}}
    genweb.webapi_v1.load_gedcom = lambda _: people
    genweb.webapi_v1.Metadata = lambda _: metadata
    genweb.genweb.Settings = MockSettings
    genweb.genweb.Metadata = MockMetadata
    genweb.genweb.People = MockPeople
    genweb.genweb.load_gedcom = lambda f: f
    api = ApiV1()
    api.load()


if __name__ == "__main__":
    test_list_people()
    test_list_metadata()
    test_get_person()
    test_get_metadata()
    test_post_metadata()
    test_non_api()
    test_metadata_404()
    test_person_404()
    test_is_call()
    test_load()
