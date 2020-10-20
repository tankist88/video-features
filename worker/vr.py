import os
import time
import wave
import json
import redis
import yt
from vosk import Model, KaldiRecognizer, SetLogLevel
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

BASE_DIR = "/youtube-audio"
MODEL_FILE = "/app/vosk-model"
TOPIC = "ytvoicerecres"

cache = redis.Redis(host='redis', port=6379, decode_responses=True)

producer = None
while producer is None:
    try:
        producer = KafkaProducer(bootstrap_servers="kafka:9092")
    except NoBrokersAvailable as err:
        print("Waiting for kafka init...")
        time.sleep(1)

SetLogLevel(0)
model = Model(MODEL_FILE)


def recognize_text(vidid):
    wav_file = BASE_DIR + "/" + vidid + "/" + vidid + ".wav"

    if not os.path.isfile(wav_file):
        yt.download_wav(vidid)

    wf = wave.open(wav_file, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        rec.AcceptWaveform(data)

    vid_text = json.loads(rec.FinalResult())["text"]
    cache.set(vidid, vid_text)
    producer.send(TOPIC, bytes(json.dumps(vid_text).encode('utf-8')))

    return vidid
