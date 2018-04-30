FROM python:3.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN mkdir ~/.ssh
ADD config ~/.ssh/

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y supervisor

COPY ./proxy.conf /etc/supervisor/conf.d/
COPY . /usr/src/app

CMD ["./supervisor.sh"]
