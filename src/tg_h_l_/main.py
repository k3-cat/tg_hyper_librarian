import inspect
import logging
import os
import sys
from importlib.util import module_from_spec, spec_from_file_location, spec_from_loader
from pathlib import Path
from typing import TYPE_CHECKING

from tg_h_l_.ruleset import Ruleset

if TYPE_CHECKING:
    from typing import Iterable

_PY_EXT = frozenset((".py",))


async def _build(module: object):
    for name, ruleset in inspect.getmembers(module):
        logging.info("ruleset:", name)
        if isinstance(ruleset, Ruleset):
            await ruleset.fetch()
            await ruleset.compile()


async def build_from_dir(dir: Path):
    for config_path in filter(lambda p: p.is_file() and p.suffix in _PY_EXT, dir.iterdir()):
        logging.info(config_path)

        module_name = f"{config_path.stem}"
        spec = spec_from_file_location(module_name, str(config_path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load spec for file {config_path}")

        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module

        await _build(module)


async def build_from_env(env_vars: Iterable[str]):
    for env_var in env_vars:
        if not (config := os.getenv(env_var, None)):
            logging.error("unable to load env:", env_var)
            continue

        logging.info("env:", env_var)

        module_name = f"{env_var}"
        spec = spec_from_loader(module_name, loader=None)
        if spec is None:
            raise ImportError(f"Could not load spec for env {env_var}")

        module = module_from_spec(spec)
        exec(config, module.__dict__)
        sys.modules[module_name] = module

        await _build(module)
