import cv2
from ultralytics import YOLO
from tracker import DroneTracker
import time

VIDEO_PATH = 'data/raw/baseline_test_01.mov' 
IMGSZ = 1280

def run_integrated_pipeline():
    model = YOLO('yolov8n.pt')
    tracker = DroneTracker(max_disappeared=30)
    cap = cv2.VideoCapture(VIDEO_PATH)
    
    # --- INITIAL TARGET SELECTION ---
    ret, first_frame = cap.read()
    print("ACTION REQUIRED: Drag a box around the DRONE and press ENTER/SPACE")
    roi = cv2.selectROI("Select Drone", cv2.resize(first_frame, (1280, 720)), fromCenter=False)
    cv2.destroyWindow("Select Drone")
    
    # Scale ROI back to original resolution
    scale_x = first_frame.shape[1] / 1280
    scale_y = first_frame.shape[0] / 720
    init_box = [roi[0]*scale_x, roi[1]*scale_y, (roi[0]+roi[2])*scale_x, (roi[1]+roi[3])*scale_y]
    
    # Seed the tracker with the manual box
    tracker.update([(init_box, "airplane")])

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        # DETECT
        results = model.predict(frame, imgsz=IMGSZ, conf=0.10, verbose=False)
        detections = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            label  = results[0].names[cls_id]
            detections.append((box.xyxy[0].tolist(), label))

        # TRACK
        tracked_box = tracker.update(detections)
        
        # VISUALIZE
        if tracked_box:
            tx1, ty1, tx2, ty2 = [int(v) for v in tracked_box]
            color = (0, 255, 0) if tracker.disappeared == 0 else (0, 255, 255)
            cv2.rectangle(frame, (tx1, ty1), (tx2, ty2), color, 3)
            label = "TRACKING" if tracker.disappeared == 0 else f"LOST: {tracker.disappeared}"
            cv2.putText(frame, label, (tx1, ty1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Show results
        cv2.imshow("Gated Kalman Tracking", cv2.resize(frame, (1280, 720)))
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_integrated_pipeline()