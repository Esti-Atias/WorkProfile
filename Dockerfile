FROM python:3.9-slim-bullseye AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libssl-dev \
    libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/static/ static/
COPY src/templates/ templates/
COPY src/app.py ./app.py
COPY src/dbcontext.py ./dbcontext.py
COPY src/person.py ./person.py
COPY src/init.sql ./init.sql 

FROM python:3.9-alpine

WORKDIR /app

RUN apk add --no-cache curl

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /app /app

EXPOSE 5000

ENTRYPOINT ["python", "app.py"]