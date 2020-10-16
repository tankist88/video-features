import os
import shutil
import atexit

from os import walk
from flask import Flask
from flask import send_file

from apscheduler.schedulers.background import BackgroundScheduler


BASE_DIR = '/youtube-audio'


def job_function():
    videos = []
    for (dirpath, dirnames, filenames) in walk(BASE_DIR):
        videos.extend(dirnames)

    rmdirs = 0
    for vid in videos:
        if not os.path.isfile(BASE_DIR + "/" + vid + "/LOCK"):
            shutil.rmtree(BASE_DIR + "/" + vid)
            rmdirs += 1

    print("rmdir count: " + str(rmdirs))


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = BASE_DIR
sched = BackgroundScheduler(daemon=True)
sched.add_job(job_function, 'cron', minute='*/10')
sched.start()


atexit.register(lambda: sched.shutdown(wait=False))


@app.route('/youtube2wav/download/<vidid>', methods=['GET'])
def download(vidid):
    link = 'https://www.youtube.com/watch?v=' + vidid
    mypath = BASE_DIR + "/" + vidid
    if os.path.isdir(mypath):
        shutil.rmtree(mypath)

    os.mkdir(mypath)
    open(mypath + "/LOCK", "w")
    os.system("youtube-dl --extract-audio -o '" + mypath + "/%(id)s.%(ext)s' " + link)
    source_file = mypath + "/" + vidid + ".opus"
    dest_file = mypath + "/" + vidid + ".wav"
    os.system("ffmpeg -i " + source_file + " -f wav -flags bitexact -ac 1 -ar 8000 -acodec pcm_s16le " + dest_file)
    os.remove(mypath + "/LOCK")

    return send_file(dest_file, mimetype="audio/wav", as_attachment=True, attachment_filename="audio.wav")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
