FROM python:3.11-slim-buster

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && \
    rm -rf /var/lib/apt/lists/*

COPY . /app/src
WORKDIR /app/src

CMD ["gunicorn", "--config", "gunicorn.py", "core_app.wsgi:application"]
