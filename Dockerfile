FROM python:3.6

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /

RUN apt update && apt install -y libav-tools

RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code
RUN pip install -r requirements.txt

ADD . /code
RUN pip install /code/

CMD ["python", "-m", "hugo"]
