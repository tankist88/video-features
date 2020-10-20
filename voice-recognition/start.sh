#!/usr/bin/env bash
chown -R 33:33 /youtube-audio
chmod -R 766 /youtube-audio
service nginx start
uwsgi --ini uwsgi.ini
