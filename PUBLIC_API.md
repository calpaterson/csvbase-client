# Public API of csvbase-client

## Specifically included

- The cli commands
- The functionality of the `csvbase.fsspec` module

## Specifically excluded

- The contents of the `csvbase.internals` module
- Textual output (ie: not csv or parquet) of cli commands like `csvbase-client
  table show`

## Otherwise

Anything not noted here should be considered excluded.
