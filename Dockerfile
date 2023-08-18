FROM python:3.11-slim-buster

ARG user=kapibara

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -U $user

USER $user:$user

COPY . /app/src
WORKDIR /app/src

CMD ["gunicorn", "--config", "gunicorn.py", "core_app.wsgi:application"]
