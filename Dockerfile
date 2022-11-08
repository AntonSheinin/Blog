FROM python:3.10-slim

RUN groupadd --gid 1000 code && \
    useradd --create-home --gid 1000 --uid 1000 code

RUN mkdir -p /home/code/blog
WORKDIR /home/code/blog

RUN apt-get update
RUN apt-get -y install gcc

COPY ./requirements.txt /home/code/blog/
RUN pip3 install -r requirements.txt

COPY ./ /home/code/blog/

RUN chown code:code /home/code/blog
USER code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV JWT_SECRET_KEY "jwt secret key"
ENV JWT_REFRESH_SECRET_KEY "jwt refresh secret key"

ENTRYPOINT uvicorn app.main:app --host 0.0.0.0 --log-level debug