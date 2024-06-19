from io import IOBase

from ._common import read_uint, read_uvarint, write_uint, write_uvarint


class Succinct:
    def __init__(self) -> None:
        self.labels: bytes
        self.label_map: bytes
        self.leaf_map: bytes

    @classmethod
    def from_collection(cls, domains):
        trie = cls()
        for domain in domains:
            print(domain)
            pass
        return trie

    def to_list(self) -> list[str]:
        result = list()
        return result

    @classmethod
    def read_from(cls, s: IOBase):
        _ = read_uint(s)  # version
        trie = cls()
        leaf_map_len = read_uvarint(s)
        trie.leaf_map = s.read(leaf_map_len * 8)
        label_map_len = read_uvarint(s)
        trie.label_map = s.read(label_map_len * 8)
        labels_len = read_uvarint(s)
        trie.labels = s.read(labels_len)

        return trie

    def write_to(self, s: IOBase):
        write_uint(s, 1)  # version
        write_uvarint(s, len(self.leaf_map) * 8)
        s.write(self.leaf_map)
        write_uvarint(s, len(self.label_map) * 8)
        s.write(self.label_map)
        write_uvarint(s, len(self.labels))
        s.write(self.labels)
