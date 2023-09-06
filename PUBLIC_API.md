# Public API of csvbase-client

## Specifically included

- The cli commands

## Specifically excluded

- The contents of the `csvbase.internals` module
- Textual output (ie: not csv or parquet) of cli commands like `csvbase-client
  table show`
- Currently, the `csvbase.fsspec` module

## Otherwise

Anything not noted here should be considered excluded.
