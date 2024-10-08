#!/usr/bin/env python3


""" Amazon AWS S3 management """


from types import SimpleNamespace
from os.path import basename

from boto3 import client

AWS_CLIENT = client


class AWS:
    """Amazon connection
    S3 https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
    """

    def __init__(self, settings):
        self.settings = settings
        self.storage = AWS_CLIENT(
            "s3",
            region_name=settings["image_s3_region"],
            aws_access_key_id=settings["aws_access_key_id"],
            aws_secret_access_key=settings["aws_secret_access_key"],
        )

    def listing(self) -> list[SimpleNamespace]:
        """Get a list of files in S3

        Returns:
            list[SimpleNamespace]: List of objects with filenames of o.Key
        """
        found = []
        params = {"Bucket": self.settings["image_s3_bucket"]}

        while True:
            results = self.storage.list_objects_v2(**params)
            found.extend(SimpleNamespace(**k) for k in results["Contents"])
            params["ContinuationToken"] = results.get("NextContinuationToken", None)

            if not results["IsTruncated"]:
                break

        return found

    def upload(self, path: str):
        """Puts an object up in S3

        Args:
            path (str): Path to the file to upload
        """
        with open(path, "rb") as contents:
            self.storage.put_object(
                ACL="public-read",
                Body=contents,
                StorageClass="STANDARD",
                Key=basename(path),
                Bucket=self.settings["image_s3_bucket"],
            )
