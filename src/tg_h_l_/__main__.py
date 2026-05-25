import argparse
import asyncio
from pathlib import Path

from tg_h_l_.main import build_from_dir, build_from_env


def __dir_path(path_str: str):
    path = Path(path_str)
    path.mkdir(mode=0o755, parents=True, exist_ok=True)

    return path


def build_arg_parser(parser: argparse.ArgumentParser):
    subparsers = parser.add_subparsers(
        title="subcommands", metavar="<command>", dest="action", required=True
    )

    build_parser = subparsers.add_parser("build", help="build configs")
    build_parser.add_argument(
        "--build-from-dir",
        type=__dir_path,
        default=Path.cwd() / "configs",
        help="The target directory path of configs",
    )
    build_parser.add_argument(
        "--build-from-env",
        nargs="+",
        help="The target env that stores config",
    )


if __name__ == "__main__":
    _parser = argparse.ArgumentParser()
    build_arg_parser(_parser)
    args = _parser.parse_args()

    if env_vars := args.build_from_env:
        asyncio.run(build_from_env(env_vars))

    else:
        asyncio.run(build_from_dir(args.build_from_dir))
