import cv2
import os

# CONFIG
VIDEO_PATH = "data/raw/baseline_test_02.mov" # Change per test
# OUTPUT_FILE will store: frame_number, x1, y1, x2, y2
OUTPUT_FILE = "data/eval/ground_truth_baseline.txt"

# State variables for mouse
drawing = False
ix, iy = -1, -1
temp_box = None

def draw_box(event, x, y, flags, param):
    global ix, iy, drawing, temp_box
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            temp_box = (ix, iy, x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        temp_box = (ix, iy, x, y)

def run_annotator():
    os.makedirs("data/eval", exist_ok=True)
    cap = cv2.VideoCapture(VIDEO_PATH)
    cv2.namedWindow("Annotator", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Annotator", draw_box)
    
    current_frame = 0
    annotations = []

    print("--- Annotation Instructions ---")
    print("Space: Save box and go to next frame")
    print("N: Skip frame (no drone visible)")
    print("Q: Quit and save progress")
    print("Drag your mouse to draw a box around the WHOLE drone.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        current_frame += 1

        # We only want to label every few frames to save time 
        # (e.g., label every 30th frame for a 1-second interval)
        if current_frame % 30 != 0:
            continue

        annotated_copy = frame.copy()
        
        while True:
            display_frame = annotated_copy.copy()
            if temp_box:
                tx1, ty1, tx2, ty2 = temp_box
                cv2.rectangle(display_frame, (tx1, ty1), (tx2, ty2), (0, 255, 0), 2)
            
            cv2.putText(display_frame, f"Frame: {current_frame} | Drawing: {drawing}", 
                        (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.imshow("Annotator", display_frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord(' '): # SAVE and next
                if temp_box:
                    x1, y1, x2, y2 = temp_box
                    annotations.append(f"{current_frame},{x1},{y1},{x2},{y2}\n")
                    print(f"Saved frame {current_frame} box: {temp_box}")
                    break
            elif key == ord('n'): # SKIP (drone not visible/ignoring)
                print(f"Skipped frame {current_frame}")
                break
            elif key == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                with open(OUTPUT_FILE, "a") as f:
                    f.writelines(annotations)
                print(f"Saved {len(annotations)} new labels to {OUTPUT_FILE}")
                return

    cap.release()
    cv2.destroyAllWindows()
    with open(OUTPUT_FILE, "a") as f:
        f.writelines(annotations)
    print(f"Finished. Saved {len(annotations)} total labels.")

if __name__ == "__main__":
    run_annotator()