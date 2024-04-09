<div align="center">
    <img alt="csvbase logo" src="https://github.com/calpaterson/csvbase/raw/main/csvbase/web/static/logo/128x128.png">
</div>

# csvbase-client

The command line client and pandas integration for [csvbase](https://csvbase.com/).

## Status

This tool is very early alpha and suitable for testing.

Semantic versioning is followed, see the [changelog](https://github.com/calpaterson/csvbase-client/blob/main/CHANGELOG.md).

## Usage

### Get a table

In pandas:

```python
>>> import pandas as pd
>>> pd.read_csv("csvbase://meripaterson/stock-exchanges")
>>> pd.read_csv("csvbase://meripaterson/stock-exchanges")
     csvbase_row_id      Continent                   Country                                     Name   MIC Last changed
0                 1         Africa                   Lesotho                                    HYBSE   NaN   2019-03-25
1                 2           Asia                Kazakhstan    Astana International Financial Centre  AIXK   2018-11-18
2                 3         Africa              South Africa                                    ZAR X  ZARX   2018-11-18
3                 4  South America                 Argentina             Bolsas y Mercados Argentinos   NaN   2018-04-02
4                 5  North America  United States of America                  Delaware Board of Trade   NaN   2018-04-02
..              ...            ...                       ...                                      ...   ...          ...
246             247  North America  United States of America                 Long-Term Stock Exchange  LTSE   2020-09-14
247             248  North America  United States of America  Miami International Securities Exchange  MIHI   2020-09-24
248             249  North America  United States of America                        Members' Exchange   NaN   2020-09-24
249             250         Africa                  Zimbabwe            Victoria Falls Stock Exchange   NaN   2020-11-01
250             251           Asia                     China                   Beijing Stock Exchange   NaN   2021-12-27

[251 rows x 6 columns]
```

From the command line

```bash
csvbase-client table get meripaterson/stock-exchanges
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

Download these from the github [release page](https://github.com/calpaterson/csvbase-client/releases/).

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
