FROM python:3.10-alpine

WORKDIR /code

RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libpq \
    libmagic

COPY ./src /code/src
COPY ./requirements/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

ARG PORT=8080
CMD ["python3", "-m", "src.main"]
