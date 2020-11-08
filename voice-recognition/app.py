import time
import redis
import json
import atexit
import requests
from flask import Flask, Response
from rq import Queue

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from apscheduler.schedulers.background import BackgroundScheduler

cache = redis.Redis(host='redis', port=6379, decode_responses=True)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
q = Queue(name="q_recognize", connection=redis.Redis(host='redis', port=6379))


def create_recognize_job(vidid):
    q.enqueue_call(func="vr.recognize_text", args=(vidid,), result_ttl=5000, timeout=600)


def consume_messages():
    consumer = None
    while consumer is None:
        try:
            consumer = KafkaConsumer(bootstrap_servers="kafka:9092",
                                     consumer_timeout_ms=1000,
                                     auto_offset_reset="latest",
                                     client_id="voice-recognition",
                                     group_id="voice-recognition",
                                     enable_auto_commit=False,
                                     auto_commit_interval_ms=1000,
                                     value_deserializer=lambda m: json.loads(m.decode("utf-8")))
            consumer.subscribe(["t_download"])
        except NoBrokersAvailable as err:
            print("Waiting for kafka init...")
            time.sleep(1)

    for message in consumer:
        print(message.value)
        create_recognize_job(message.value["vidid"])
    consumer.commit()


sched = BackgroundScheduler(daemon=True)
sched.add_job(consume_messages, 'cron', second='*/10')
sched.start()

atexit.register(lambda: sched.shutdown(wait=False))


@app.route('/voice-recognition/enqueue/<vidid>', methods=['GET'])
def rec_enqueue(vidid):
    res = requests.get("http://youtube2wav:8080/youtube2wav/download/enqueue/" + vidid)
    result = json.dumps({"status": "success" if res.status_code == 200 else "fail"}, ensure_ascii=False, indent=4)
    return Response(result, content_type="application/json; charset=utf-8")


@app.route('/voice-recognition/text/<vidid>', methods=['GET'])
def gettext(vidid):
    result = json.dumps({"status": "success", "text": cache.get(vidid)}, ensure_ascii=False, indent=4)
    return Response(result, content_type="application/json; charset=utf-8")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
