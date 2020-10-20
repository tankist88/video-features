import redis
import json
from flask import Flask, Response
from rq import Queue

cache = redis.Redis(host='redis', port=6379, decode_responses=True)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
q = Queue(connection=redis.Redis(host='redis', port=6379))


@app.route('/voice-recognition/enqueue/<vidid>', methods=['GET'])
def rec_enqueue(vidid):
    job = q.enqueue_call(
        func="vr.recognize_text", args=(vidid,), result_ttl=5000, timeout=600
    )
    result = json.dumps({"status": "success", "jobId": job.get_id()}, ensure_ascii=False, indent=4)
    return Response(result, content_type="application/json; charset=utf-8")


@app.route('/voice-recognition/text/<vidid>', methods=['GET'])
def gettext(vidid):
    result = json.dumps({"status": "success", "text": cache.get(vidid)}, ensure_ascii=False, indent=4)
    return Response(result, content_type="application/json; charset=utf-8")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
