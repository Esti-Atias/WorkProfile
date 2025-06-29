FROM python:3.9-slim-buster 


 WORKDIR /app 


 COPY requirements.txt . 

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libssl-dev \
    libffi-dev && \
    rm -rf /var/lib/apt/lists/*

 RUN pip install --no-cache-dir -r requirements.txt 

 COPY static/ static/ 

 COPY templates/ templates/ 

 COPY app.py . 

 COPY dbcontext.py . 

 COPY person.py . 


 EXPOSE 5000 


 CMD ["python", "app.py"]
