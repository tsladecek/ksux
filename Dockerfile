FROM python:3.11.2-alpine

ARG VERSION

RUN apk add --no-cache build-base

RUN pip install --upgrade pip && pip install ksux==$VERSION
