import shutil
import io
from pathlib import Path
import sys
from logging import DEBUG, basicConfig

import toml
import click

from .cache import TableCache
from .config import get_config, write_config, config_path


def get_version() -> str:
    return (Path(__file__).resolve().parent.parent / "VERSION").open().read()


def verbose_logging() -> None:
    basicConfig(level=DEBUG, stream=sys.stderr, format="%(message)s")


@click.group("cbc")
@click.version_option(version=get_version())
@click.option("--verbose", is_flag=True, help="Enable more verbose output (to stderr).")
def cli(verbose: bool):
    """A cli client for csvbase."""
    # FIXME: guard this under --verbose
    if verbose:
        verbose_logging()


@cli.group(help="Read and write from tables.")
def tables():
    ...


@cli.command()
def login():
    """Write API credentials to config file, creating it if necessary."""
    config = get_config()
    username = click.prompt(
        "Please enter your username", default=config.username, show_default=True
    )
    api_key = click.prompt("Please enter your API key", hide_input=True)
    config.username = username
    config.api_key = api_key

    table_cache = TableCache()
    are_valid = table_cache.check_creds(config)
    if are_valid:
        write_config(config)
        click.echo(f"Wrote {config_path()}")
    else:
        click.echo(
            click.style(
                "ERROR: Username or API key rejected by server - double check"
                " they're both correct!",
                fg="red",
            )
        )
        exit(1)


@tables.command(help="Get a table.")
@click.argument("ref")
@click.option(
    "--force-cache-miss",
    is_flag=True,
    default=False,
    help="Always download the table again, even if it hasn't changed",
)
def get(ref: str, force_cache_miss: bool):
    table_cache = TableCache()
    table_buf = table_cache.get_table(ref, force_miss=force_cache_miss)
    text_buf = io.TextIOWrapper(table_buf, encoding="utf-8")
    shutil.copyfileobj(text_buf, sys.stdout)


@tables.command(help="Show metadata about a table")
@click.argument("ref")
def show(ref: str):
    table_cache = TableCache()
    metadata = table_cache.metadata(ref)
    rv = {
        ref: {
            "caption": metadata["caption"],
            "created": metadata["created"],
            "last_changed": metadata["last_changed"],
            "etag": metadata["etag"],
        }
    }

    toml.dump(rv, sys.stdout)


# NOTE: This is for convenience only, the cli is actually called by setup.py
# entry_points
if __name__ == "__main__":
    cli()
