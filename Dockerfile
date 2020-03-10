FROM python:3.8-slim

COPY . /app

RUN pip install --trusted-host pypi.python.org -r app/requirements.txt