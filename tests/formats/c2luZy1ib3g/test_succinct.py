import pytest
from bitarray import bitarray
from tg_hyper_librarian.formats.c2luZy1ib3g.succinct import Succinct, _find_ith_one, _set_bit

BASIC_TEST_DATA1 = [
    ("", (42, False), ""),
    (
        "0000000000000000000000000000000000000000000000000000000000000000",
        (15, True),
        "0000000000000001000000000000000000000000000000000000000000000000",
    ),
    (
        "",
        (64, True),
        (
            "0000000000000000000000000000000000000000000000000000000000000000"
            "1000000000000000000000000000000000000000000000000000000000000000"
        ),
    ),
    (
        "0100100100000101001000000010001000100010110110010101001001001010",
        (4, False),
        "0100000100000101001000000010001000100010110110010101001001001010",
    ),
]

BASIC_TEST_DATA2 = [
    ("01000100010001", 3, 9),
    (
        (
            "0101101010100010100101010101011010101010101010101101010100010101"
            "0110101010101101101010101010101101110111011010101101111101011010"
        ),
        33,
        66,
    ),
]


@pytest.mark.basic
class TestSuccinctBasis:
    @pytest.mark.parametrize("bits01, val, expected01", BASIC_TEST_DATA1)
    def test_set_bit(self, bits01: str, val: tuple[int, bool], expected01: str):
        bits = bitarray(bits01)
        _set_bit(bits, val[0], val[1])
        assert bits.to01() == expected01

    @pytest.mark.parametrize("bits01, i, index", BASIC_TEST_DATA2)
    def test_find_ith_one(self, bits01: bitarray, i: int, index: int):
        bits = bitarray(bits01)
        assert _find_ith_one(bits, i) == index


TEST_DATA = [
    (
        ["", "a"],
        "1100000000000000000000000000000000000000000000000000000000000000",
        "0110000000000000000000000000000000000000000000000000000000000000",
        "a",
    ),
    (
        ["a", "b", "c"],
        "0111000000000000000000000000000000000000000000000000000000000000",
        "0001111000000000000000000000000000000000000000000000000000000000",
        "abc",
    ),
    (
        ["a", "ab", "abc"],
        "0111000000000000000000000000000000000000000000000000000000000000",
        "0101011000000000000000000000000000000000000000000000000000000000",
        "abc",
    ),
    (
        ["abc", "abcd", "abd", "abde", "bc", "bcd", "bcde", "cde"],
        "0000010111111100000000000000000000000000000000000000000000000000",
        "0001010101001010101010111110000000000000000000000000000000000000",
        "abcbcdcddedee",
    ),
    (
        [
            "A",
            "Aani",
            "Aaron",
            "Aaronic",
            "Aaronical",
            "Aaronite",
            "Aaronitic",
            "Aaru",
            "Ab",
            "Ababdeh",
            "Ababua",
            "Abadite",
            "Abama",
            "Abanic",
            "Abantes",
            "Abarambo",
            "Abaris",
            "Abasgi",
            "Abassin",
            "Abatua",
            "Abba",
            "Abbadide",
            "Abbasside",
            "Abbie",
            "Abby",
            "Abderian",
            "Abderite",
            "Abdiel",
            "Abdominales",
            "Abe",
            "Abel",
            "Abelia",
            "Abelian",
            "Abelicea",
            "Abelite",
            "Abelmoschus",
            "Abelonian",
            "Abencerrages",
            "Aberdeen",
            "Aberdonian",
            "Aberia",
            "Abhorson",
        ],
        (
            "0101000001010100000001010001000100010000000001000000000000101001"
            "1010001010000000101011101000001010000000101101101000101111001000"
            "0011101000000000000000000000000000000000000000000000000000000000"
        ),
        (
            "0100100100000101001000000010001000100010110110010101001001001010"
            "0101101010100010100101010101011010101010101010101101010100010101"
            "0100101010010110110101110110101001101010101010101010110101001111"
            "0110101010101101101010101010101101110111011010101101111101011010"
            "1010101111011000000000000000000000000000000000000000000000000000"
        ),
        (
            "Aabnrabdehioubdmnrstaiyeiolnronduiaitaigsudseremimocdirieatcemsi"
            "iaisiliactoneeoascthesbndiatnneesirenoaeioedneaacarninlcelhnaaeugnsses"
        ),
    ),
]


@pytest.mark.parametrize("domains, leaf_map01, label_map01, labels", TEST_DATA)
class TestSuccinct:
    def test_from_list(self, domains: list[str], leaf_map01: str, label_map01: str, labels: str):
        trie = Succinct.from_list(domains)
        assert trie._leaf_map.to01() == leaf_map01
        assert trie._label_map.to01() == label_map01
        assert trie._labels == labels

    def test_to_list(self, domains: list[str], leaf_map01: str, label_map01: str, labels: str):
        trie = Succinct(bitarray(leaf_map01), bitarray(label_map01), labels)
        assert trie.to_list() == domains
