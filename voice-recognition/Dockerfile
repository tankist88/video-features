FROM python:3.8

RUN apt-get update -y
RUN apt-get install -y python3-dev build-essential nginx

RUN \
mkdir -p /app && \
chown -R 33:33 /app && \
chmod 744 /app

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt --src /usr/local/src

COPY app.py /app
COPY uwsgi.ini /app
COPY start.sh /app
COPY nginx.conf /etc/nginx

RUN chmod +x ./start.sh

CMD ["./start.sh"]