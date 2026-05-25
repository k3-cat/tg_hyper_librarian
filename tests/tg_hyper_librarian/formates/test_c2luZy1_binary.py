from tg_h_l_.formates.c2luZy1_binary import _BINARY_AUTO_FIELDS, _SOURCE_AUTO_FIELDS


class TestC2luZy1Binary:
    def test_field_anno(self):
        assert _SOURCE_AUTO_FIELDS
        assert _BINARY_AUTO_FIELDS

    def test_field_coverage(self):
        assert _SOURCE_AUTO_FIELDS - _BINARY_AUTO_FIELDS == frozenset()
