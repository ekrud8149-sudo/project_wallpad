from flask import Flask, Response
import cv2
import threading
import time

app = Flask(__name__)

# 최신 화면을 저장할 전역 변수
global_frame = None
camera = cv2.VideoCapture(0) # 카메라 번호 (안 나오면 1, 2로 변경)

# 해상도 설정
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 15)

# [핵심] 백그라운드에서 계속 사진을 찍어서 변수에 저장함
def update_frame():
    global global_frame
    while True:
        success, frame = camera.read()
        if success:
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                global_frame = buffer.tobytes()
        time.sleep(0.01)

# 쓰레드 시작 (서버 켜지자마자 촬영 시작)
t = threading.Thread(target=update_frame)
t.daemon = True
t.start()

# 1. 동영상 주소 (계속 보냄)
@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            if global_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n')
            time.sleep(0.05)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 2. 사진 주소 (한 장만 보냄) -> 이게 있어야 에러가 안 남!
@app.route('/snap')
def snap():
    if global_frame:
        return Response(global_frame, mimetype='image/jpeg')
    else:
        return "Camera loading...", 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
