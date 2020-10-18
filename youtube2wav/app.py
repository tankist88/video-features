import os
import shutil
import atexit
import redis
import json

from datetime import datetime
from os import walk
from flask import Flask, Response, send_file

from apscheduler.schedulers.background import BackgroundScheduler

from rq import Queue
from rq.job import Job

BASE_DIR = "/youtube-audio"
LOCK_PERIOD_HOURS = 1

cache = redis.Redis(host='redis', port=6379)
app = Flask(__name__)
q = Queue(connection=cache)


def clean_video():
    videos = []
    for (dirpath, dirnames, filenames) in walk(BASE_DIR):
        videos.extend(dirnames)

    rm_dirs = 0
    for vid in videos:
        lock_file_path = BASE_DIR + "/" + vid + "/LOCK"
        if not os.path.isfile(lock_file_path):
            continue

        lock_file = open(lock_file_path, "r")
        create_time = datetime.strptime(lock_file.read(), "%Y.%m.%d %H:%M:%S")
        lock_file.close()

        if ((datetime.now() - create_time).total_seconds() / 60 / 60) > LOCK_PERIOD_HOURS:
            shutil.rmtree(BASE_DIR + "/" + vid)
            rm_dirs += 1

    print("Remove video count: " + str(rm_dirs))


sched = BackgroundScheduler(daemon=True)
sched.add_job(clean_video, 'cron', minute='*/10')
sched.start()

atexit.register(lambda: sched.shutdown(wait=False))


@app.route('/youtube2wav/download/enqueue/<vidid>', methods=['GET'])
def download_enqueue(vidid):
    job = q.enqueue_call(
        func="yt.download_wav", args=(vidid,), result_ttl=5000
    )
    result = json.dumps({"status": "success", "jobId": job.get_id()}, ensure_ascii=False, indent=4)
    return Response(result, content_type="application/json; charset=utf-8")


@app.route('/youtube2wav/download/result/<job_key>', methods=['GET'])
def download_result(job_key):
    job = Job.fetch(job_key, connection=cache)

    if job.is_finished:
        dest_file = BASE_DIR + "/" + job.result + "/" + job.result + ".wav"
        return send_file(dest_file, mimetype="audio/wav", as_attachment=True, attachment_filename="audio.wav")
    else:
        result = json.dumps({"status": "IN PROGRESS"}, ensure_ascii=False, indent=4)
        return Response(result, content_type="application/json; charset=utf-8")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
