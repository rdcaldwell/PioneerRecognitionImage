from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from flask import Flask, render_template, Response, jsonify
from webcam import VideoCamera
import os
import recognizer
import cv2
import uuid
import time
import requests

app = Flask(__name__, instance_relative_config=True)
dir = os.path.dirname(__file__)
global_frame = None

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recognize/')
def recognize():
    cam = cv2.VideoCapture(0)
    return_value, image = cam.read()
    cam.release()
    image_file = "/+"+ str(uuid.uuid4()) + ".png"
    image_path = "/static" + image_file
    file_path = os.path.join(dir, 'static') + image_file
    cv2.imwrite(file_path, image)
    recognizer.label_image(file_path)
    while not os.path.exists(file_path):
        time.sleep(1)
    return render_template('recognize.html', image_url=image_path, labels=recognizer.labels, results=recognizer.results, top_k=recognizer.top_k)


@app.route('/left')
def left():
    return jsonify(requests.get('http://localhost:8080/left').text)


@app.route('/right')
def right():
    return jsonify(requests.get('http://localhost:8080/right').text)


@app.route('/frwrd')
def frwrd():
    return jsonify(requests.get('http://localhost:8080/forward').text)


@app.route('/back')
def back():
    return jsonify(requests.get('http://localhost:8080/backward').text)


@app.route('/accl')
def accl():
    return jsonify(requests.get('http://localhost:8080/accelerate').text)


@app.route('/decel')
def slow():
    return jsonify(requests.get('http://localhost:8080/decelerate').text)


def video_stream():
    global global_frame
    video_camera = VideoCamera()
    while True:
        frame = video_camera.get_frame()
        if frame is not None:
            global_frame = frame
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='127.0.0.1', threaded=True)
