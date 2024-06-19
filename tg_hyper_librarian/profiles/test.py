from pathlib import Path

from ..formats.c2luZy1ib3g import load_from_c2luZy1ib3g


def generate_at(root_dir: Path):
    with open(root_dir / "common1.srs", "rb") as fp:
        group = load_from_c2luZy1ib3g(fp)
        print(group)
