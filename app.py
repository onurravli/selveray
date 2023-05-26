import RPi.GPIO as GPIO # Bu paket default olarak Raspberry Pi'lar uzerinde yuklu gelir
import cv2 # OpenCV paketi
from flask import Flask, render_template, Response
from time import sleep

# Step motora bagli GPIO pinleri
coil_A_1_pin = 17
coil_A_2_pin = 27
coil_B_1_pin = 22
coil_B_2_pin = 23

# Camera ayarlari
camera = cv2.VideoCapture(0)  # Change the camera index if needed

# GPIO ayarlari
GPIO.setmode(GPIO.BCM)
GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)

# Flask uygulamasi
app = Flask(__name__)


# HTML sayfasi icin default route
@app.route('/')
def index():
    return render_template('index.html')


# Step motoru saat yonunde hareket ettiren fonksiyon
def move_clockwise():
    set_step(1, 0, 0, 1)
    sleep(0.01)
    set_step(0, 1, 0, 1)
    sleep(0.01)
    set_step(0, 1, 1, 0)
    sleep(0.01)
    set_step(1, 0, 1, 0)
    sleep(0.01)


# Step motoru saat yonunun tersine hareket ettiren fonksiyon
def move_counter_clockwise():
    set_step(1, 0, 1, 0)
    sleep(0.01)
    set_step(0, 1, 1, 0)
    sleep(0.01)
    set_step(0, 1, 0, 1)
    sleep(0.01)
    set_step(1, 0, 0, 1)
    sleep(0.01)


# Step motoru durduran fonksiyon
def stop_motor():
    set_step(0, 0, 0, 0)


# GPIO pinlerini ayarlayan fonksiyon
def set_step(w1, w2, w3, w4):
    GPIO.output(coil_A_1_pin, w1)
    GPIO.output(coil_A_2_pin, w2)
    GPIO.output(coil_B_1_pin, w3)
    GPIO.output(coil_B_2_pin, w4)


# Video stream fonksiyonu
def camera_stream():
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# Video feed route
@app.route('/video_feed')
def video_feed():
    return Response(camera_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Motor hareketleri icin route'lar
@app.route('/forward')
def forward():
    move_clockwise()
    return 'Moving Forward'


@app.route('/backward')
def backward():
    move_counter_clockwise()
    return 'Moving Backward'


@app.route('/left')
def left():
    move_counter_clockwise()
    return 'Turning Left'


@app.route('/right')
def right():
    move_clockwise()
    return 'Turning Right'


@app.route('/stop')
def stop():
    stop_motor()
    return 'Stopping'


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
