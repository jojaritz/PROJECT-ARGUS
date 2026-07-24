import cv2
from ultralytics import YOLO
import time

# CONFIGURATION
VIDEO_PATH = "data/raw/baseline_test_02.mov"
INFERENCE_RES = 1280
CROP_SIZE = 1280

# Start with a short portion of the video for visual testing.
# Set to None later when you intentionally want the whole clip.
MAX_FRAMES = None  # Set to None to process the entire video.


def run_center_crop_detection():
    model = YOLO("yolov8n.pt")

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print(f"Error: Could not open {VIDEO_PATH}")
        return

    frame_count = 0
    total_inference_ms = 0.0

    print("Starting center-crop inference test...")
    print("Press 'q' while the preview window is selected to stop early.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Reached end of video.")
            break

        frame_count += 1

        if MAX_FRAMES is not None and frame_count > MAX_FRAMES:
            print(f"Stopped after configured limit of {MAX_FRAMES} frames.")
            break

        # Original frame is 3840 x 2160.
        # This extracts a 1280 x 1280 region centered in the frame.
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2

        x1 = cx - CROP_SIZE // 2
        y1 = cy - CROP_SIZE // 2
        x2 = cx + CROP_SIZE // 2
        y2 = cy + CROP_SIZE // 2

        crop = frame[y1:y2, x1:x2]

        inference_start = time.perf_counter()

        results = model.predict(
            crop,
            imgsz=INFERENCE_RES,
            conf=0.15,
            verbose=False,
        )

        inference_ms = (time.perf_counter() - inference_start) * 1000
        total_inference_ms += inference_ms

        annotated_crop = results[0].plot()

        cv2.putText(
            annotated_crop,
            f"Frame: {frame_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            annotated_crop,
            f"Inference: {inference_ms:.1f} ms",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            annotated_crop,
            "Press q to quit",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        cv2.imshow("YOLO Center-Crop Test", annotated_crop)

        # Required for the OpenCV window to refresh and accept key input.
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("Stopped by user.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if frame_count > 0:
        average_inference_ms = total_inference_ms / frame_count
        print("\n--- Center-Crop Test Complete ---")
        print(f"Frames processed: {frame_count}")
        print(f"Average inference time: {average_inference_ms:.1f} ms")


if __name__ == "__main__":
    run_center_crop_detection()