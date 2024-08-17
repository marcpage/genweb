#!/usr/bin/env python3


""" Test the V1 web api """


from json import loads, dumps
from types import SimpleNamespace
from io import BytesIO

from genweb.webapi_v1 import ApiV1


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
    def __init__(self, **fields):
        self.saved = False
        super().__init__(fields)

    def save(self):
        self.saved = True


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
    post_metadata = {"a": 1, "b": 2, "people": "a,b, c\r\nd\ne f;g:h", "c": ""}
    handler.set_body(dumps(post_metadata).encode("utf-8"))
    body, mime, code = api.handle_post(handler)
    metadata = loads(body)
    assert set(metadata) == set(post_metadata) - {"c"}, body
    assert metadata["a"] == post_metadata["a"], body
    assert metadata["b"] == post_metadata["b"], body
    assert "c" not in metadata, body
    assert set(metadata["people"]) == set("abcdefgh"), body
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
