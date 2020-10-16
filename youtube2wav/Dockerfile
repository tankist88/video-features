FROM python:3.8

RUN apt-get update -y
RUN apt-get install -y python3-dev build-essential ffmpeg curl nginx

RUN \
curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl && \
chmod a+rx /usr/local/bin/youtube-dl && \
mkdir -p /youtube-audio && \
mkdir -p /app

RUN \
chown -R 33:33 /youtube-audio && \
chmod -R 766 /youtube-audio

VOLUME /youtube-audio

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt --src /usr/local/src

COPY app.py /app
COPY uwsgi.ini /app
COPY start.sh /app
COPY nginx.conf /etc/nginx

RUN chmod +x ./start.sh

CMD ["./start.sh"]