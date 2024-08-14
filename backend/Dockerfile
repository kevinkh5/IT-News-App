FROM python:3.12

WORKDIR /usr/src/flask_app
RUN mkdir -p /usr/src/flask_app/audio
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./app.py .
COPY ./wsgi.py .
COPY ./.env .