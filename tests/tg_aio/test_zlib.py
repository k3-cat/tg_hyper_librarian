import zlib
from io import BytesIO

import pytest

from tg_aio.io import AsyncBytesIO, AsyncZlibReader, AsyncZlibWriter

PLAIN_TEXT = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing "
    "elit, sed do eiusmod tempor incididunt ut labore et "
    "dolore magna aliqua. Ut enim ad minim veniam, quis "
    "nostrud exercitation ullamco laboris nisi ut aliquip ex "
    "ea commodo consequat. Duis aute irure dolor in "
    "reprehenderit in voluptate velit esse cillum dolore eu "
    "fugiat nulla pariatur. Excepteur sint occaecat "
    "cupidatat non proident, sunt in culpa qui officia "
    "deserunt mollit anim id est laborum."
    "\n"
    "こはやとゅ知ツニレサユむさ譜屋保擢こょしるぬたなら舳樹け課巣の、"
    "氏魔津か毛無ゅも。ょ以り譜課しはたはミュタやぬゅみ目御"
    "ラニミオのゅやヤヤトミ毛素フハ「ミ、舳都雲毛」無知これかにま雲手区"
    "以根尾模さもせゃれ区露個無むよさつ樹巣区。"
).encode("utf-8")

COMPRESSED_TEXT = zlib.compress(PLAIN_TEXT)


class TestZlibIO:
    @pytest.mark.asyncio
    async def test_read(self):
        async with AsyncBytesIO(BytesIO(COMPRESSED_TEXT)) as fp, AsyncZlibReader(fp) as zfp:
            text = await zfp.read()

        assert text == PLAIN_TEXT

    @pytest.mark.asyncio
    async def test_read_incremental(self):
        text = bytearray()
        async with AsyncBytesIO(BytesIO(COMPRESSED_TEXT)) as fp, AsyncZlibReader(fp) as zfp:
            while data := await zfp.read(64):
                text += data

        assert bytes(text) == PLAIN_TEXT

    @pytest.mark.asyncio
    async def test_write(self):
        mem = BytesIO()
        async with AsyncBytesIO(mem) as fp, AsyncZlibWriter(fp) as zfp:
            await zfp.write(PLAIN_TEXT)

        assert mem.getvalue() == COMPRESSED_TEXT

    @pytest.mark.asyncio
    async def test_write_incremental(self):
        raw_bytes = BytesIO(PLAIN_TEXT)
        mem = BytesIO()
        async with AsyncBytesIO(mem) as fp, AsyncZlibWriter(fp) as zfp:
            while data := raw_bytes.read(64):
                await zfp.write(data)

        assert mem.getvalue() == COMPRESSED_TEXT
