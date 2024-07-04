from contextlib import contextmanager
from io import BufferedReader, BufferedWriter
from typing import Any, Generator, Mapping

import boto3


class R2:
    name = "R2"

    def __init__(self, info: Mapping[str, Any]) -> None:
        self._bucket = boto3.client(
            "s3",
            endpoint_url=f"https://{info["account_id"]}.r2.cloudflarestorage.com",
        ).Bucket(info["bucket_name"])

    @contextmanager
    def fetch(self, path: str) -> Generator[BufferedReader]:
        resp = self._bucket.Object(key=path).get()
        try:
            yield resp["Body"]
        finally:
            resp.close()

    @contextmanager
    def push(self, path: str) -> Generator[BufferedWriter]:
        raise NotImplementedError()

    def push_bytes(self, path: str, content: bytes):
        raise NotImplementedError()
