<div align="center">
    <img alt="csvbase logo" src="https://github.com/calpaterson/csvbase/raw/main/csvbase/web/static/logo/128x128.png">
</div>

# csvbase-client

The command line client for [csvbase](https://csvbase.com/).

## Status

This tool is very early alpha and suitable for testing.

## Usage

### Get a table

```bash
csvbase-client table get meripaterson/stock-exchanges
```

Outputs CSV to stdout:

```
csvbase_row_id,Continent,Country,Name,MIC,Last changed
1,Africa,Lesotho,HYBSE,,2019-03-25
2,Asia,Kazakhstan,Astana International Financial Centre,AIXK,2018-11-18
3,Africa,South Africa,ZAR X,ZARX,2018-11-18
[ full file omitted ]
```

### Set (aka "upsert") a table:

```bash
csvbase-client table set meripaterson/stock-exchanges stock-exchanges.csv
```

Nothing is output upon success and exit code is 0.

## Installing

### Executable

Download these from the github release page.

### Pip + PyPI

```bash
pip install csvbase-client
```

### Docker

```bash
docker pull calpaterson/csvbase-client
```

Then when you run:

```bash
# mount your own xdg-cache directory as a volume inside the container
docker run -v "${XDG_CACHE_HOME:-$HOME/.cache}":/root/.cache calpaterson/csvbase-client
```
