FROM python:3.7-alpine

WORKDIR /app

COPY ./requirements.txt .

RUN apk add --no-cache build-base && \
    pip install -r requirements.txt --disable-pip-version-check && \
    apk del build-base

COPY entrypoint.py .
COPY ./natscli/ .

ENTRYPOINT ["/usr/local/bin/python", "/app/entrypoint.py"]

CMD ["--help"]
