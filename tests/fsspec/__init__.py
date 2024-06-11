import duckdb
import fsspec

duckdb.register_filesystem(fsspec.filesystem("csvbase"))
