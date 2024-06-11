# Changelog

All notable changes to `csvbase-client` will be documented in this file. This
project adheres to [Semantic Versioning](https://semver.org/).

To understand what falls under the category of the public API and what lies
outside it, please consult [PUBLIC_API.md](PUBLIC_API.md). Changes that do not
impact the public API usually will not lead to a version change and might not
be mentioned here.

## Unreleased

## [0.1.1] - 2024-04-10

### Added

- Python 3.12 support

### Fixed

- Adding missing dependency on importlib_resources

## [0.1.0] - 2024-04-09

### Added
- A working fsspec implementation
  - Pandas, Dask and Polars actively tested and supported
- A way to inspect (and clear) the cache - `csvbase-client cache --help`

### Removed
- Most of the pre-fsspec code is gone

## [0.0.1] - 2023-08-30

### Added
- Initial implementation of csvbase-client.
