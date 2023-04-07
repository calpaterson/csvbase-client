from typing import Optional
from dataclasses import dataclass, fields
from pathlib import Path
import functools
from logging import getLogger

import toml

from .dirs import dirs

logger = getLogger(__name__)


@dataclass
class Config:
    base_url: str
    username: Optional[str]
    api_key: Optional[str]


DEFAULT_CONFIG = Config(base_url="https://csvbase.com/", username=None, api_key=None)


def config_path() -> Path:
    return Path(dirs.user_config_dir) / "config.toml"


@functools.lru_cache(1)
def get_config() -> Config:
    path = config_path()
    if not path.exists():
        logger.info(
            "config file does not exist, returning default config: %s", DEFAULT_CONFIG
        )
        return DEFAULT_CONFIG
    else:
        parsed = toml.load(path.open())
        config = Config(
            base_url=parsed.get("base_url", DEFAULT_CONFIG.base_url),
            username=parsed.get("username", DEFAULT_CONFIG.username),
            api_key=parsed.get("api_key", DEFAULT_CONFIG.api_key),
        )
        return config


def write_config(config: Config) -> None:
    path = config_path()
    if not path.exists():
        path.parent.mkdir(exist_ok=True, parents=True)

    writeout_dict = {}
    for field in fields(Config):
        default_value = getattr(DEFAULT_CONFIG, field.name)
        our_value = getattr(config, field.name)
        if our_value != default_value:
            writeout_dict[field.name] = our_value

    with path.open("w", encoding="utf-8") as config_buffer:
        toml.dump(writeout_dict, config_buffer)
