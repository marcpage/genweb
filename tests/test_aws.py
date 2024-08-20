#!/usr/bin/env python3

""" Test AWS """


from genweb.aws import AWS
import genweb.aws


class MockS3:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.params_list_objects_v2 = None
        self.params_put_object = None

    @staticmethod
    def client(kind: str, **kwargs):
        assert kind == "s3", f"invalid kind: {kind}"
        return MockS3(**kwargs)

    def list_objects_v2(self, **kwargs) -> dict:
        self.params_list_objects_v2 = kwargs
        return {"Contents": [{"Key": "filename.ext"}], "IsTruncated": False}

    def put_object(self, **kwargs):
        self.params_put_object = kwargs
        self.params_put_object["Body"] = kwargs["Body"].read()


def test_basic() -> None:
    genweb.aws.AWS_CLIENT = MockS3.client
    settings = {
        "image_s3_region": "region",
        "aws_access_key_id": "key",
        "aws_secret_access_key": "secret",
        "image_s3_bucket": "bucket",
    }
    aws = AWS(settings)
    found = aws.listing()
    assert len(found) == 1
    assert found[0].Key == "filename.ext"
    aws.upload(__file__)
    assert b"Kragle" in aws.storage.params_put_object["Body"]


if __name__ == "__main__":
    test_basic()
