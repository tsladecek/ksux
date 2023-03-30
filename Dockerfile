FROM python:3.11.2-alpine

ARG VERSION

RUN pip install --upgrade pip && pip install ksux==$VERSION
