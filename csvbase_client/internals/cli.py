import shutil
import sys
from logging import DEBUG, basicConfig, WARNING
from typing import IO

import humanize
import fsspec
import click
from rich.console import Console as RichConsole
from rich.table import Table as RichTable

from .config import config_path
from .version import get_version
from .cache import cache_path, get_fs_cache, cache_contents


@click.group("csvbase-client")
@click.version_option(version=get_version())
@click.option("--verbose", is_flag=True, help="Enable more verbose output (to stderr).")
def cli(verbose: bool):
    """A cli client for csvbase."""
    if verbose:
        level = DEBUG
    else:
        level = WARNING
    basicConfig(level=level, stream=sys.stderr, format="%(levelname)s: %(message)s")


@cli.group("table", help="Interact with tables")
def table(): ...


@cli.command()
def info():
    """Show the configuration file location, and the contents"""
    exist_str = "" if config_path().exists() else " (does not exist)"
    click.echo(f"config path: {config_path()}{exist_str}")
    exist_str = "" if cache_path().exists() else " (does not exist)"
    click.echo(f"cache path: {cache_path()}{exist_str}")


@cli.group(help="Manage the local cache")
def cache(): ...


@cache.command("show", help="Show cache location and contents")
def cache_show() -> None:
    table = RichTable(
        title="csvbase-client cache", caption=f"Cache path: {cache_path()}"
    )
    table.add_column("Ref")
    table.add_column("ETag prefix")
    table.add_column("Last read")
    table.add_column("Size")

    for ce in cache_contents(get_fs_cache()):
        # for now, only some of the CacheEntry data is surfaced
        table.add_row(
            ce.ref,
            ce.etag_prefix(),
            humanize.naturaltime(ce.last_read),
            humanize.naturalsize(ce.size_bytes, gnu=True),
        )

    console = RichConsole()
    console.print(table)


@cache.command("clear", help="Wipe the cache")
def clear() -> None:
    fs_cache = get_fs_cache()
    fs_cache.clear()


# @cli.command()
# def login():
#     """Write API credentials to config file, creating it if necessary."""
#     config = get_config()
#     username = click.prompt(
#         "Please enter your username", default=config.username, show_default=True
#     )
#     api_key = click.prompt("Please enter your API key", hide_input=True)
#     config.username = username
#     config.api_key = api_key

#     table_cache = TableCache()
#     are_valid = table_cache.check_creds(config)
#     if are_valid:
#         write_config(config)
#         click.echo(f"Wrote {config_path()}")
#     else:
#         click.echo(
#             click.style(
#                 "ERROR: Username or API key rejected by server - double check"
#                 " they're both correct!",
#                 fg="red",
#             )
#         )
#         exit(1)


@table.command(help="Get a table.")
@click.argument("ref")
@click.option(
    "--force-cache-miss",
    is_flag=True,
    default=False,
    help="Always download the table again, even if it hasn't changed",
)
def get(ref: str, force_cache_miss: bool):
    fs = fsspec.filesystem("csvbase")
    table_buf = fs.open(ref, "r")
    shutil.copyfileobj(table_buf, sys.stdout)


# @table.command("show", help="Show metadata about a table")
# @click.argument("ref")
# def table_show(ref: str):
#     table_cache = TableCache(get_config())
#     metadata = table_cache.metadata(ref, auth=get_auth())
#     rv = {
#         ref: {
#             "caption": metadata["caption"],
#             "created": metadata["created"],
#             "last_changed": metadata["last_changed"],
#         }
#     }

#     click.echo(toml.dumps(rv))


@table.command("set", help="Create or upsert a table.")
@click.argument("ref")
@click.argument("file", type=click.File("rb"))
def set(ref: str, file: IO[str]):
    fs = fsspec.filesystem("csvbase")
    with fs.open(ref, "wb") as table_buf:
        shutil.copyfileobj(file, table_buf)


# NOTE: This is for convenience only, the cli is actually called by setup.py
# entry_points
if __name__ == "__main__":
    cli()
