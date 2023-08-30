import shutil
import io
from pathlib import Path
import sys
from logging import DEBUG, basicConfig, WARNING
from typing import IO
import csv
import importlib.resources as imp_resources

import toml
import click

import csvbase_client
from .auth import get_auth
from .cache import TableCache, cache_path
from .config import get_config, write_config, config_path
from .version import get_version


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


@cli.group("table", help="Read and write from tables.")
def table():
    ...


@cli.command()
def config():
    """Show the configuration file location, and the contents"""
    exist_str = "" if config_path().exists() else " (does not exist)"
    click.echo(f"config path: {config_path()}{exist_str}")
    exist_str = "" if cache_path().exists() else " (does not exist)"
    click.echo(f"config path: {cache_path()}{exist_str}")


@cli.group(help="Manage the local cache")
def cache():
    ...


@cache.command("show", help="Show cache location and contents")
@click.option(
    "--full-urls",
    default=False,
    is_flag=True,
    help="Show full urls (hint: some terminals make them clickable)",
)
def cache_show(full_urls: bool):
    table_cache = TableCache(get_config())
    tsv_writer = csv.writer(sys.stdout, dialect="excel-tab")
    common_cols = ["last_modified", "content_type", "etag (prefix)"]
    if full_urls:
        header = ["url"]
    else:
        header = ["ref"]
    header.extend(common_cols)
    tsv_writer.writerow(header)

    prefix_length = len(table_cache.base_url())
    for url, etag, content_type, last_modified in table_cache.entries():
        # FIXME: not quite a ref - includes file extension
        if full_urls:
            a = url
        else:
            a = url[prefix_length:]
        etag_prefix = etag[3:13]
        tsv_writer.writerow([a, last_modified, content_type.mimetype(), etag_prefix])


@cache.command("clear", help="Wipe the cache")
def clear():
    table_cache = TableCache(get_config())
    table_cache.clear()


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


@table.command(help="Get a table.")
@click.argument("ref")
@click.option(
    "--force-cache-miss",
    is_flag=True,
    default=False,
    help="Always download the table again, even if it hasn't changed",
)
def get(ref: str, force_cache_miss: bool):
    table_cache = TableCache(get_config())
    table_buf = table_cache.get_table(ref, force_miss=force_cache_miss, auth=get_auth())
    text_buf = io.TextIOWrapper(table_buf, encoding="utf-8")
    shutil.copyfileobj(text_buf, sys.stdout)


@table.command(help="Show metadata about a table")
@click.argument("ref")
def table_show(ref: str):
    table_cache = TableCache(get_config())
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


@table.command(help="Upsert a table.")
@click.argument("ref")
@click.argument("file", type=click.File("rb"))
def set(ref: str, file: IO[str]):
    table_cache = TableCache(get_config())
    table_cache.set_table(ref, file)


# NOTE: This is for convenience only, the cli is actually called by setup.py
# entry_points
if __name__ == "__main__":
    cli()
