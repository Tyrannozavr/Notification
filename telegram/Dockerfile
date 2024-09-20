FROM python:3.10-slim as builder
RUN mkdir /usr/src/app
RUN mkdir /usr/src/app/media
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt


COPY . /usr/src/app/

CMD ["python", "main.py"]