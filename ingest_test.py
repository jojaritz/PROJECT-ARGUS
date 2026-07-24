import cv2
import time
import os

# CONFIGURATION
VIDEO_PATH = 'data/raw/baseline_test_01.mov' # Update extension if needed
DISPLAY_SCALE = 0.25 # 4K is huge; scale down for display only

def run_ingest_test():
    if not os.path.exists(VIDEO_PATH):
        print(f"Error: Could not find video at {VIDEO_PATH}")
        return

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print(f"Error: OpenCV could not open {VIDEO_PATH}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Video metadata: {width}x{height}, {fps:.2f} fps, {frame_total} frames")
    
    frame_count = 0 
    start_time = time.perf_counter()

    print(f"Starting ingest test on {VIDEO_PATH}...")
    
    while cap.isOpened():
        # MODULE 01: INGEST
        loop_start = time.perf_counter()
        
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # SIMULATE PIPELINE OVERHEAD (placeholder for Detector/Tracker)
        # We just scale for display to check basic performance
        h, w = frame.shape[:2]
        display_frame = cv2.resize(frame, (int(w * DISPLAY_SCALE), int(h * DISPLAY_SCALE)))
        
        # MODULE 04: LOGGING/TELEMETRY (On-screen for now)
        loop_end = time.perf_counter()
        processing_time_ms = (loop_end - loop_start) * 1000
        
        cv2.putText(display_frame, f"Frame: {frame_count}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(display_frame, f"Proc Time: {processing_time_ms:.2f}ms", (20, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('Drone Observation System - Phase 0 Ingest', display_frame)
        
        # Press 'q' to exit early
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    total_time = time.perf_counter() - start_time
    avg_fps = frame_count / total_time
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("--- Test Complete ---")
    print(f"Total Frames: {frame_count}")
    print(f"Average Throughput: {avg_fps:.2f} FPS")

if __name__ == "__main__":
    run_ingest_test()