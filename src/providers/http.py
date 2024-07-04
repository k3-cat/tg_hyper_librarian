from contextlib import contextmanager
from io import BufferedWriter
from typing import Any, BinaryIO, Generator, Mapping

import urllib3


class Http:
    def __init__(
        self, num_pools: int = 10, headers: Mapping[str, str] | None = None, **connection_pool_kw: Any
    ) -> None:
        self._http = urllib3.PoolManager(num_pools, headers, **connection_pool_kw)
        self._job_count = 0

    @contextmanager
    def fetch(self, url: str) -> "Generator[BinaryIO]":
        self._job_count += 1
        job_id = self._job_count
        print(f"> [{job_id}] downloading {url}")
        resp = self._http.request(
            "GET",
            url,
            preload_content=False,
        )
        try:
            yield resp  # type: ignore
        finally:
            print(f"... done [{job_id}]")
            resp.release_conn()

    @contextmanager
    def push(self, url: str) -> "Generator[BufferedWriter]":
        raise NotImplementedError()

    def push_bytes(self, url: str, content: bytes):
        self._http.request("POST", url, content)
