import time
import redis
import json
import wave
import urllib
import atexit
import os
from vosk import Model, KaldiRecognizer, SetLogLevel
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from flask import Flask, Response
from os import walk

from apscheduler.schedulers.background import BackgroundScheduler

WAV_FILES_VOLUME = "/wavfiles"
MODEL_FILE = "/app/vosk-model"
TOPIC = "ytvoicerecres"
IN_PROGRESS_STATUS = "<-IN PROGRESS->"

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


def get_text(wav_file):
    wf = wave.open(WAV_FILES_VOLUME + "/" + wav_file, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        rec.AcceptWaveform(data)
    return json.loads(rec.FinalResult())["text"]


def job_function():
    wav_files = []
    for (dirpath, dirnames, filenames) in walk(WAV_FILES_VOLUME):
        wav_files.extend(filenames)
        break

    print("Files to recognize: " + str(len(wav_files)))

    for wav_file in wav_files:
        vidid = wav_file.split(".")[0]
        vid_text = cache.get(vidid)

        if vid_text is None:
            cache.set(vidid, IN_PROGRESS_STATUS)
            vid_text = get_text(wav_file)
            cache.set(vidid, vid_text)
        elif vid_text == IN_PROGRESS_STATUS:
            print("Video " + vidid + " IN PROGRESS. Skip.")
            continue

        producer.send(TOPIC, bytes(json.dumps(vid_text).encode('utf-8')))

        print("Video " + vidid + " DONE")
        os.remove(WAV_FILES_VOLUME + "/" + wav_file)


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
sched = BackgroundScheduler(daemon=True)
sched.add_job(job_function, 'cron', minute='*/1')
sched.start()


atexit.register(lambda: sched.shutdown(wait=False))


@app.route('/voice-recognition/schedule/<vidid>', methods=['GET'])
def schedule(vidid):
    urllib.request.urlretrieve(
        'http://youtube2wav:8080/youtube2wav/download/' + vidid,
        WAV_FILES_VOLUME + '/' + vidid + '.wav')

    result = json.dumps({"status": "success"}, ensure_ascii=False, indent=4)
    return Response(result, content_type="application/json; charset=utf-8")


@app.route('/voice-recognition/text/<vidid>', methods=['GET'])
def gettext(vidid):
    result = json.dumps({"status": "success", "text": cache.get(vidid)}, ensure_ascii=False, indent=4)
    return Response(result, content_type="application/json; charset=utf-8")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
