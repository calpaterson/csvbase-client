from pathlib import Path

import click

from .cache import TableCache


def get_version() -> str:
    return (Path(__file__).resolve().parent.parent / "VERSION").open().read()


@click.group("csvbasec")
@click.version_option(version=get_version())
def cli():
    """A cli client for csvbase(.com)."""
    # FIXME: guard this under --verbose
    import sys
    from logging import DEBUG, basicConfig

    basicConfig(level=DEBUG, stream=sys.stderr)
    ...


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
