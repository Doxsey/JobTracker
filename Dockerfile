FROM python:3.12.1-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends openssh-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r /app/requirements.txt

COPY ./app /app

EXPOSE 5050

CMD ["gunicorn","--config", "app/gunicorn_config.py", "app:create_app()"]