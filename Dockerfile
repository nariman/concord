FROM python:latest

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /

RUN apt update
RUN apt install -y libav-tools

RUN mkdir /hugo
WORKDIR /hugo

ADD requirements.txt /hugo
RUN pip install -r requirements.txt

ADD . /hugo

CMD ["python", "bootstrap.py"]
