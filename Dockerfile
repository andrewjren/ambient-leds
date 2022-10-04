# syntax=docker/dockerfile:1
FROM python:3.9-slim

# set READTHEDOCS to true to allow installing picamera onto image
ENV READTHEDOCS=True
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# install gcc
RUN apt-get update
RUN apt-get -y install gcc

# install python requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["waitress-serve", "app:app"]