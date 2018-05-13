from flask import Flask, request, jsonify

import recognizer
import os
import threading
import requests

dir = os.path.dirname(__file__)
app = Flask(__name__, instance_relative_config=True)
interval = 300


@app.route('/api/image/recognize', methods=['POST'])
def recognize():
    file = request.files['image']
    file_path = os.path.join(dir, 'static', 'img.jpg')
    file.save(file_path)
    recognizer.label_image(file_path)
    json = {
        'labels': recognizer.labels,
        'results': recognizer.results.tolist(),
        'top_k': recognizer.top_k.tolist()
    }
    return jsonify(json)


def start_timer():
    threading.Timer(interval, start_timer).start()
    print('Pinging heroku...')
    requests.get('https://imagerecognitionrobot.herokuapp.com')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    start_timer()