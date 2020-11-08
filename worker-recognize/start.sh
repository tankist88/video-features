#!/usr/bin/env bash
chown -R 33:33 /youtube-audio
chmod -R 766 /youtube-audio
/usr/bin/supervisord -c /app/supervisord.conf