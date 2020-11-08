import time
import os
import shutil
import json

from datetime import datetime

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

BASE_DIR = '/youtube-audio'
TOPIC = "t_download"

producer = None
while producer is None:
    try:
        producer = KafkaProducer(bootstrap_servers="kafka:9092")
    except NoBrokersAvailable as err:
        print("Waiting for kafka init...")
        time.sleep(1)


def download_wav(vidid):
    link = 'https://www.youtube.com/watch?v=' + vidid
    my_path = BASE_DIR + "/" + vidid

    if os.path.isdir(my_path):
        shutil.rmtree(my_path)

    os.mkdir(my_path)

    lock_file = open(my_path + "/LOCK", "w")
    lock_file.write(datetime.now().strftime("%Y.%m.%d %H:%M:%S"))
    lock_file.close()

    os.system("youtube-dl --extract-audio -o '" + my_path + "/%(id)s.%(ext)s' " + link)
    source_file = my_path + "/" + vidid + ".opus"
    dest_file = my_path + "/" + vidid + ".wav"
    os.system("ffmpeg -i " + source_file + " -f wav -flags bitexact -ac 1 -ar 8000 -acodec pcm_s16le " + dest_file)

    event = {
        "type": "downloaded",
        "vidid": vidid
    }

    producer.send(TOPIC, bytes(json.dumps(event).encode('utf-8')))

    print(event)

    return vidid
