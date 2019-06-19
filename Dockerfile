FROM python:3.7-alpine

WORKDIR /app

COPY ./requirements.txt .
COPY ./setup.py .

RUN apk add --no-cache build-base && \
    pip install -r requirements.txt --disable-pip-version-check && \
    apk del build-base

COPY ./entrypoint.py .
COPY ./stancli/ ./stancli/

ENTRYPOINT ["/usr/local/bin/python", "/app/entrypoint.py"]

CMD ["--help"]
