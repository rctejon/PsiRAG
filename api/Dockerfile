# syntax=docker/dockerfile:1

FROM python:3.9.19

WORKDIR /api
RUN mkdir -p ../data

RUN apt-get update && apt-get install -y chromium-driver && apt-get install -y chromium && apt-get clean

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD templates templates

COPY app.py app.py

EXPOSE 5000

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "-w", "4"]