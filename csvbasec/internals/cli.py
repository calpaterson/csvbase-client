from pathlib import Path

import click
import requests


def get_version() -> str:
    return (Path(__file__).resolve().parent.parent / "VERSION").open().read()


@click.group("csvbasec")
@click.version_option(version=get_version())
def cli():
    """A cli client for csvbase(.com)."""
    ...


@cli.group(help="Read and write from tables.")
def table():
    ...


@table.command(help="Get a table.")
@click.argument("ref")
def get(ref: str):
    url = f"https://csvbase.com/{ref}"
    response = requests.get(url, headers={"Accept": "text/csv"})
    response.raise_for_status()
    click.echo(response.text, nl=False)


# NOTE: This is for convenience only, the cli is actually called by setup.py
# entry_points
if __name__ == "__main__":
    cli()
