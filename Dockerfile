# syntax=docker/dockerfile:1.4
FROM python:3.11-slim-bookworm as builder
RUN apt-get update && apt-get -y upgrade
RUN pip install build
COPY ./ ./
RUN python -m build .

FROM python:3.11-slim-bookworm
COPY --from=builder dist/*.whl .
RUN python -m pip --no-cache-dir install *.whl
ENTRYPOINT ["csvbase-client"]
