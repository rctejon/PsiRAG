# syntax=docker/dockerfile:1

FROM python:3.9.19

WORKDIR /rag-api

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD templates templates

COPY app.py app.py
COPY llm.py llm.py
COPY chunking.py chunking.py
ADD .env .env

EXPOSE 5000

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "-w", "4"]