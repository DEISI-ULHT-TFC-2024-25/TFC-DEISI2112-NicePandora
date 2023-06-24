FROM --platform=linux/amd64 ubuntu:focal


RUN cat etc/os-release

RUN apt update
RUN apt install -y apt-transport-https ca-certificates curl gnupg lsb-release dpkg

RUN lsb_release -cs
RUN dpkg --print-architecture

RUN apt install -y python3 python3-pip docker.io 

  # dependencies for building Python packages
RUN apt install -y libpq-dev

RUN python3 --version

WORKDIR /

#COPY ./app /app
#COPY ./docker /docker
#COPY ./.env/ /.env

COPY ./requirements.txt /requirements.txt
COPY ./docker/entrypoint /entrypoint
COPY ./docker/start /start
COPY ./docker/worker_entrypoint /worker_entrypoint

#WORKDIR /app


RUN pip install --upgrade pip
RUN pip install gunicorn
RUN pip install -r requirements.txt


RUN chmod 755 /entrypoint
RUN chmod 755 /worker_entrypoint
RUN chmod 755 /start

ENTRYPOINT ["/entrypoint"]
