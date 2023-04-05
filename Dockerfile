# syntax=docker/dockerfile:1.4
FROM python:3.11-slim-buster as builder
RUN apt-get update && apt-get -y upgrade
RUN pip install build
COPY ./ ./
RUN python -m build .

FROM python:3.11-slim-buster
COPY csvbasec/VERSION .version
COPY --from=builder dist/*.whl .
RUN python -m pip --no-cache-dir install *.whl
ENTRYPOINT ["csvbasec"]
