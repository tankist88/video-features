FROM python:3.8

RUN apt-get update -y
RUN apt-get install -y python3-dev build-essential ffmpeg curl supervisor

RUN \
curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl && \
chmod a+rx /usr/local/bin/youtube-dl && \
mkdir -p /app && \
chown -R 33:33 /app && \
chmod 744 /app && \
mkdir -p /app/log && \
chown -R 33:33 /app/log && \
chmod 766 /app/log && \
mkdir -p /app/run && \
chown -R 33:33 /app/run && \
chmod 766 /app/run && \
mkdir -p /app/log/supervisord && \
chown -R 33:33 /app/log/supervisord && \
chmod 766 /app/log/supervisord

WORKDIR /app

COPY vosk-model /app/vosk-model
COPY requirements.txt /app
RUN pip install -r requirements.txt --src /usr/local/src

COPY yt.py /app
COPY vr.py /app
COPY worker.py /app
COPY supervisord.conf /app
COPY start.sh /app

RUN chmod +x ./start.sh

CMD ["./start.sh"]