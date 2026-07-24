import cv2
import numpy as np
from ultralytics import YOLO

# CONFIGURATION
# This MUST be the exact video used to create GROUND_TRUTH_FILE.
VIDEO_PATH = "data/raw/baseline_test_01.mov"
GROUND_TRUTH_FILE = "data/eval/ground_truth_baseline_1.txt"

MODEL_PATH = "yolov8n.pt"
IMGSZ = 1280
CONFIDENCE_THRESHOLD = 0.15
IOU_PASS_THRESHOLD = 0.60


def calculate_iou(box_a, box_b):
    """
    Calculate Intersection over Union (IoU).

    Each box format is: [x1, y1, x2, y2]
    """

    x_left = max(box_a[0], box_b[0])
    y_top = max(box_a[1], box_b[1])
    x_right = min(box_a[2], box_b[2])
    y_bottom = min(box_a[3], box_b[3])

    intersection_width = max(0, x_right - x_left)
    intersection_height = max(0, y_bottom - y_top)
    intersection_area = intersection_width * intersection_height

    area_a = max(0, box_a[2] - box_a[0]) * max(0, box_a[3] - box_a[1])
    area_b = max(0, box_b[2] - box_b[0]) * max(0, box_b[3] - box_b[1])

    union_area = area_a + area_b - intersection_area

    if union_area <= 0:
        return 0.0

    return intersection_area / union_area


def load_ground_truth(file_path):
    """
    Load annotations in this format:
    frame_number,x1,y1,x2,y2

    Returns:
        Dictionary in this format:
        {frame_number: [x1, y1, x2, y2]}
    """

    ground_truth = {}

    try:
        with open(file_path, "r") as file:
            for line_number, line in enumerate(file, start=1):
                parts = line.strip().split(",")

                if len(parts) != 5:
                    print(
                        f"Skipping malformed line {line_number}: "
                        f"{line.strip()}"
                    )
                    continue

                try:
                    frame_number = int(parts[0])
                    box = [int(value) for value in parts[1:]]
                    ground_truth[frame_number] = box
                except ValueError:
                    print(
                        f"Skipping non-numeric line {line_number}: "
                        f"{line.strip()}"
                    )

    except FileNotFoundError:
        print(f"Error: Ground-truth file was not found: {file_path}")
        return {}

    return ground_truth


def run_evaluation():
    ground_truth = load_ground_truth(GROUND_TRUTH_FILE)

    print(
        f"Loaded {len(ground_truth)} ground-truth annotations "
        f"from {GROUND_TRUTH_FILE}"
    )

    if not ground_truth:
        print(
            "No valid annotations were found. "
            "Check that the file path is correct and contains labels."
        )
        return

    model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print(f"Error: Could not open video: {VIDEO_PATH}")
        return

    frame_index = 0
    iou_results = []

    print(f"Evaluating {len(ground_truth)} annotated frames...")

    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            break

        frame_index += 1

        if frame_index not in ground_truth:
            continue

        ground_truth_box = ground_truth[frame_index]

        predictions = model.predict(
            frame,
            imgsz=IMGSZ,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False,
        )

        best_iou = 0.0
        best_class_name = "no detection"
        best_confidence = 0.0

        for predicted_box in predictions[0].boxes:
            predicted_coordinates = predicted_box.xyxy[0].tolist()
            current_iou = calculate_iou(
                ground_truth_box,
                predicted_coordinates,
            )

            if current_iou > best_iou:
                best_iou = current_iou

                class_id = int(predicted_box.cls[0].item())
                best_class_name = predictions[0].names[class_id]
                best_confidence = float(predicted_box.conf[0].item())

        iou_results.append(best_iou)

        status = (
            "PASS"
            if best_iou >= IOU_PASS_THRESHOLD
            else "FAIL"
        )

        print(
            f"Frame {frame_index}: "
            f"IoU = {best_iou:.3f} [{status}] | "
            f"Best class = {best_class_name} | "
            f"Confidence = {best_confidence:.3f}"
        )

    cap.release()

    if not iou_results:
        print(
            "No annotated frame numbers were encountered in the video. "
            "The annotations may belong to a different source video."
        )
        return

    median_iou = float(np.median(iou_results))
    success_rate = (
        sum(iou >= IOU_PASS_THRESHOLD for iou in iou_results)
        / len(iou_results)
        * 100
    )
    total_misses = sum(iou == 0.0 for iou in iou_results)

    print("\n--- FINAL EVALUATION RESULTS ---")
    print(f"Annotated frames evaluated: {len(iou_results)}")
    print(f"Median IoU: {median_iou:.3f}")
    print(
        f"Success Rate (IoU >= {IOU_PASS_THRESHOLD:.2f}): "
        f"{success_rate:.1f}%"
    )
    print(f"Total Misses (IoU = 0): {total_misses}")


if __name__ == "__main__":
    run_evaluation()