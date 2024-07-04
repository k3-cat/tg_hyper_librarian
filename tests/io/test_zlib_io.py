import zlib
from io import BytesIO

from tg_hyper_librarian.io import ZlibReaderIO, ZlibWriterIO

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
    def test_read(self):
        text1 = ZlibReaderIO(BytesIO(COMPRESSED_TEXT)).read()
        assert text1 == PLAIN_TEXT

        text2 = bytearray()
        zsp = ZlibReaderIO(BytesIO(COMPRESSED_TEXT))
        while data := zsp.read(64):
            text2 += data
        assert bytes(text2) == PLAIN_TEXT

    def test_write(self):
        bytes1 = BytesIO()
        with ZlibWriterIO(bytes1) as zsp:
            zsp.write(PLAIN_TEXT)
        assert bytes1.getvalue() == COMPRESSED_TEXT

        raw_bytes = BytesIO(PLAIN_TEXT)

        bytes2 = BytesIO()
        with ZlibWriterIO(bytes2) as zsp:
            while data := raw_bytes.read(64):
                zsp.write(data)
        assert bytes2.getvalue() == COMPRESSED_TEXT
