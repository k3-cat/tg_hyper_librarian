from pathlib import Path

import boto3


class S3:
    def __init__(self, account_id: str, bucket_name: str) -> None:
        self._bucket = boto3.client(
            "s3",
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        ).Bucket(bucket_name)

    def put_object(self, path: Path) -> None:
        with path.open("rb") as fp:
            self._bucket.put_object(Key=path.name, Body=fp)
