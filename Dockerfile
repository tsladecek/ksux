FROM python:3.12.3-alpine

ARG VERSION

RUN apk add --no-cache build-base

RUN pip install --upgrade pip && pip install ksux==$VERSION
