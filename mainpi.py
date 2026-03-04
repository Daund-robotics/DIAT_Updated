import cv2
import torch
import numpy as np
from PIL import Image
from flask import Flask, render_template, Response, jsonify
import threading
import time

app = Flask(__name__)

# Load YOLOv5 model - Explicitly set to CPU for Raspberry Pi 4
print("Loading YOLOv5 neural network engine...")
model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', source='github')
model.cpu()  # Force execution on CPU for ARM architecture
print("Model loaded successfully.")

classes = ['Drone']
# Default static rectangle coordinates
rectangle_coords = [(50, 50), (250, 50), (250, 250), (50, 250)]

# Global status mapping
alert_system = {
    "warning": False,
}

latest_frame = None
lock = threading.Condition()

def process_camera():
    global latest_frame, alert_system
    # Initialize the camera using index 0 (standard USB/Pi webcams)
    cap = cv2.VideoCapture(0)
    
    # Raspberry Pi Pi Camera optimizations (lower resolution for faster processing)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    # Target 30fps capture
    cap.set(cv2.CAP_PROP_FPS, 30)

    # Note: On a Pi 4 CPU, running a YOLO model is heavy.
    # size=320 runs faster than size=640 at the cost of detection range/accuracy.
    inference_size = 320 
    
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        # Inference format conversion
        img = Image.fromarray(frame[...,::-1])
        results = model(img, size=inference_size)
        
        warning_flag = False

        # Process the results and draw bounding boxes on the frame
        for result in results.xyxy[0]:
            x1, y1, x2, y2, conf, cls = result.tolist()
            if conf > 0.5 and classes[int(cls)] in classes:
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                text_conf = "{:.2f}%".format(conf * 100)
                cv2.putText(frame, text_conf, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                text_coords = "({}, {})".format(int((x1 + x2) / 2), int(y2))
                cv2.putText(frame, text_coords, (int(x1), int(y2) + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # Check if the drone intersects with or is inside the rectangle
                if rectangle_coords[0] != rectangle_coords[1]:
                    x_mid = (x1 + x2) / 2
                    y_mid = (y1 + y2) / 2
                    # Basic bounding box intersection check with static rectangle area
                    if rectangle_coords[0][0] <= x_mid <= rectangle_coords[2][0] and rectangle_coords[0][1] <= y_mid <= rectangle_coords[2][1]:
                        warning_flag = True
                        cv2.putText(frame, "Warning: Drone Detected Under Restricted Area!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Draw the rectangle
        for i in range(4):
            cv2.circle(frame, rectangle_coords[i], 5, (0, 255, 0), -1)
            cv2.line(frame, rectangle_coords[i], rectangle_coords[(i+1)%4], (0, 255, 0), 2)

        # Encode frame back to JPEG string
        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            with lock:
                latest_frame = buffer.tobytes()
                alert_system["warning"] = warning_flag
                lock.notify_all()

# Start Daemon Thread
camera_thread = threading.Thread(target=process_camera, daemon=True)
camera_thread.start()

def generate_frames():
    global latest_frame
    while True:
        with lock:
            lock.wait()
            frame_bytes = latest_frame
            
        if frame_bytes is not None:
            # Yield frame in a multipart boundary for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    with lock:
        warning_state = alert_system["warning"]
    return jsonify({"warning": warning_state})

if __name__ == "__main__":
    # Get local IP to display the correct URL
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"
        
    print("\n" + "="*60)
    print(f"  SYSTEM READY: Open your browser to -> http://{local_ip}:5000  ")
    print("="*60 + "\n")

    # Removed debug=True for Pi 4 to save memory, binding to 0.0.0.0 to enable access from the Pi's local network IP
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
