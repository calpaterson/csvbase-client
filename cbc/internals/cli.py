from pathlib import Path
import sys
from logging import DEBUG, basicConfig

import click

from .cache import TableCache


def get_version() -> str:
    return (Path(__file__).resolve().parent.parent / "VERSION").open().read()


def verbose_logging() -> None:
    basicConfig(level=DEBUG, stream=sys.stderr, format="%(message)s")


@click.group("cbc")
@click.version_option(version=get_version())
@click.option("--verbose", is_flag=True)
def cli(verbose: bool):
    """A cli client for csvbase."""
    # FIXME: guard this under --verbose
    if verbose:
        verbose_logging()


@cli.group(help="Read and write from tables.")
def table():
    ...


@table.command(help="Get a table.")
@click.argument("ref")
def get(ref: str):
    table_cache = TableCache()
    table = table_cache.get_table(ref)
    click.echo(table, nl=False)


# NOTE: This is for convenience only, the cli is actually called by setup.py
# entry_points
if __name__ == "__main__":
    cli()
