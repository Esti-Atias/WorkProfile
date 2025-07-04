FROM python:3.9-slim-buster AS builder

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


COPY static/ static/
COPY templates/ templates/
COPY app.py dbcontext.py person.py ./

# =============================================================================


FROM python:3.9-alpine

WORKDIR /app


COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

COPY --from=builder /app /app

EXPOSE 5000

ENTRYPOINT ["python", "app.py"]
