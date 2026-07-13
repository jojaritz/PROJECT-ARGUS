# PROJECT_CONTEXT.md

## 1. Mission Statement

Design and evaluate a safe, non-contact aerial-target observation system that detects and tracks a cooperative DJI Mini 2 SE drone in real time. The system will estimate the drone’s image-space position and motion, log its performance, and later provide estimates that can aim an observation camera or non-hazardous illumination source toward the drone without contacting or interfering with it.

## 2. System Scope and Boundaries

### In scope

- Detecting a DJI Mini 2 SE drone from stationary camera footage.
- Tracking the drone’s position and motion in image coordinates.
- Measuring detection accuracy, throughput, latency, and target retention.
- Logging system estimates and evaluation results.
- Future non-contact camera pointing or illumination aiming based on the estimated target location.
- Testing from recorded video before integrating live video capture.

### Out of scope

- Any projectile, launch, firing, physical contact, interception, or interference with the drone.
- Autonomous drone flight control.
- Identification of people, vehicles, or unrelated targets.
- Claims of reliable operation outside the defined test conditions without measured evidence.

## 3. Hardware and Development Stack

| Category | Current plan |
|:---|:---|
| Primary workstation | Windows 11 desktop with NVIDIA RTX 2080 |
| Mobile/development system | MacBook Pro with M1 Pro |
| Primary live-camera candidate | Sony FDR-AX33 camcorder |
| Secondary live-camera candidate | Canon EOS R50 with RF-S 18–45 mm lens |
| Baseline data camera | iPhone 13 Mini main camera |
| Initial test target | DJI Mini 2 SE, stock configuration |
| Planned live-video interface | USB 3 HDMI capture device, pending acquisition and acceptance testing |
| Development environment | Python, VS Code, OpenCV, NumPy, PyTorch/Ultralytics YOLO |
| Initial input data | iPhone 13 Mini video recorded at 3840×2160, 60 fps |

## 4. Baseline Test Conditions

- Primary environment: outdoor park with trees and houses in the background.
- Lighting window: approximately 10:00 AM to 6:00 PM.
- Camera mounting: stationary tripod or static structure.
- Drone operation: a second person can operate the drone.
- Initial target range: approximately 20–100 ft.
- Stretch target range: up to 500 ft, subject to image-quality and detection evidence.
- Phase 1 includes clear-sky, cluttered-background, lateral-motion, and limited-occlusion test cases.


## 5. Current Evidense

Experiment 0.11 — Offline iPhone Video Ingest Baseline

| Measurement | Result |
|:---|:---|
| Host system | M1 Pro MacBook Pro |
| Source camera | iPhone 13 Mini main camera |
| Video dimensions | 3840 × 2160 |
| Source frame rate | 60.00 fps |
| Total video frames | 2,075 |
| Full preview-loop throughput | 39.16 fps |
| Observed decode + resize time | Typically 9–10 ms; occasional peaks near 14 ms |
| Drone visibility | Visually identifiable throughout the baseline clip |
| Farthest observed target footprint | Approximately 56 × 26 pixels at 4K |


Initial Finding: Small-Target Detection Risk
At the farthest point, the drone is approximately 56 × 26 pixels in a 4K frame. Resizing the full 3840-pixel-wide frame to YOLO’s common 640-pixel-wide input would reduce the drone to roughly 9 × 4 pixels.

This is likely insufficient for reliable stock-model detection. Phase 1 must evaluate detector input resolution, cropping, and tiled inference rather than assuming default 640 × 640 inference is appropriate.


## 6. Performance Targets — Version 0.1

| ID | Metric | Initial requirement | Measurement definition |
|:---|:---|:---|:---|
| PERF-01 | Localization accuracy | Median IoU ≥ 0.60 | Compare the estimated drone bounding box with a human-labeled ground-truth bounding box on frames where the drone is visible. |
| PERF-02 | Software pipeline latency | Median frame-arrival-to-tracker-output time ≤ 33 ms | Measure software processing time from frame ingestion to the tracker producing its state estimate. Camera and capture-device delay are excluded until live testing begins. |
| PERF-03 | Target continuity | No loss longer than 15 consecutive frames at 30 fps | During defined test conditions, the system must not lack both an accepted detector measurement and a valid tracker estimate for more than approximately 0.5 seconds. |


 ## 7. Module Definitions

Module 01 — Frame Ingest
 - Purpose: Acquire frames from either a recorded video file or, later, a live camera/capture-card stream.

 - Input: Video file or live camera stream.

 - Output: Raw image frame in BGR format, frame index, source timestamp, and local processing timestamp.

 - Initial responsibility: Maintain a current-frame pipeline that avoids building a backlog of stale frames.

Module 02 — Drone Detector
 - Purpose: Use an object-detection model, initially YOLO, to locate the DJI Mini 2 SE in each image.

 - Input: Image frame from Module 01.

 - Output: One or more candidate detections containing a bounding box, class label, and confidence score.

 - Initial responsibility: Determine whether a stock detector can reliably detect the drone at the required image size. If not, evaluate higher-         resolution, crop-based, tiled, or custom-trained approaches.

Module 03 — Tracker and State Estimator
 - Purpose: Associate detections over time and estimate the drone’s current image-space position and motion.

 - Input: Detector outputs, timestamps, and prior estimated state.

 - Output: Filtered target position, estimated velocity, track status, and prediction confidence.

 - Future interface: Provide a non-contact pointing estimate to a pan-tilt observation camera or non-hazardous illumination system. This module does     not command, contact, or interfere with the drone.

Module 04 — Logger and Evaluator
 - Purpose: Store telemetry and calculate evidence-based performance metrics.

 - Input: Frame timestamps, detections, tracker estimates, system timing data, and human-labeled ground truth.

 - Output: CSV or JSON telemetry files, IoU accuracy metrics, latency metrics, target-loss events, and test summaries.

 - Initial responsibility: Make every performance claim reproducible from recorded data.

## 8. Initial Risk Register

| ID | Risk | Category | Why it matters | Initial mitigation |
|:---|:---|:---|:---|:---|
| R-01 | The drone becomes too small for reliable detection at longer ranges. | Technical | At the farthest point in the baseline video, the target is only about 56 × 26 pixels at 4K. Full-frame downscaling can reduce it below detectable size. | Measure detection performance at multiple input resolutions; evaluate cropped or tiled inference; establish a measured maximum operating range. |
| R-02 | Background clutter, especially trees, causes missed detections and incorrect classifications. | Technical / environmental | Stock YOLO frequently failed to identify the drone against trees, including some close-range passes. Incorrect labels included `train`, `bench`, `bear`, `bird`, and `kite`. | Establish sky-background operation as the Phase 1 baseline. Collect and label representative tree-background footage. Evaluate camera settings, optical zoom, custom drone-specific training, and tracker-based association before claiming tree-background reliability. |
| R-03 | Capture, decoding, inference, tracking, display, or logging creates excessive latency. | Technical / integration | A delayed target estimate becomes less useful for real-time observation and later camera pointing. | Timestamp each module boundary; profile offline processing first; later measure capture-to-output latency with live hardware; process the newest frame rather than queueing old frames. |
| R-04 | Stock YOLO weights do not recognize the drone reliably. | Technical / model | A general-purpose detector may not have enough examples of a small DJI Mini 2 SE against varied sky and ground backgrounds. | Establish a stock-model baseline; label a representative dataset if needed; compare model, image-resolution, and training approaches using the same evaluation clips. |
| R-05 | Live HDMI capture is unstable, limited to a lower frame rate, or adds large delay. | Hardware / integration | Offline video success does not prove live-camera performance. | Conduct a capture-card acceptance test: verify recognition, resolution, frame rate, stability for 10 minutes, disconnects, freezes, and measured delay. |
| R-06 | The detector may produce false `bird` or `kite` detections from propellers, branches, or other small moving visual features. | Technical / model | False positives could cause the tracker to follow the wrong object or report incorrect target continuity. | Log class, confidence, box size, and position for every detection; later test association rules and motion-based tracking against labeled video. |


## 9. Phase plan

Phase 0 — Requirements and Architecture
 - Define scope, safety boundaries, hardware options, requirements, modules, risks, and measurement strategy.
 - Complete camera/capture-interface audit.
 - Record initial offline-video ingest evidence.

Phase 1 — Offline Detection and Tracking
 - Run a stock YOLO baseline on recorded footage.
 - Establish an appropriate inference resolution for the small target.
 - Add tracking and timestamped telemetry.
 - Label evaluation frames and calculate IoU, continuity, and software latency metrics.
 - Primary supported test condition: approximately 20–50 ft range with a predominantly sky background.
 - Challenging measurement conditions: tree background, mixed background, and 50–100 ft range.
 - Tree-background and longer-range results will be recorded as stress-test evidence, not treated as initially supported operating conditions.

Phase 2 — Live Video Ingest
 - Integrate HDMI capture hardware.
 - Validate resolution, frame rate, signal stability, and end-to-end delay.
 - Run the Phase 1 pipeline using live video.

Phase 3 — Non-Contact Pointing
 - Use tracker output as an input to a pan-tilt observation camera or non-hazardous illumination system.
 - Measure pointing accuracy and response delay.
 - Preserve the project’s non-contact safety boundary.

Phase 4 — Multi-Camera Localization
 - Add synchronized camera streams.
 - Investigate 3D localization and triangulation.
 - Evaluate calibration accuracy and multi-camera tracking performance.

 ### Experiment 1.1 — Stock YOLO Feasibility Baseline
| Measurement | Result |
|:---|:---|
| Host system | M1 Pro MacBook Pro |
| Input video | iPhone 13 Mini main camera, 3840 × 2160, 60 fps |
| Model | Ultralytics YOLOv8 Nano (`yolov8n.pt`) |
| Detector input size | 1280 pixels |
| Detection result | Drone detected in favorable sky/cloud scenes |
| Observed predicted class | Record exact displayed YOLO class label |
| Typical inference time | Approximately 75 ms per frame |
| Brief worst observed inference time | Over 100 ms |
| Approximate inference rate | Approximately 13 fps at typical inference time |
| Sky/cloud performance | Generally accurate; occasional kite classification |
| Tree-background performance | Drone not detected reliably |
| False positives | Birds were sometimes classified as kites |
| Result | Partial pass: stock model demonstrates feasibility in favorable scenes, but does not meet the latency target on the M1 Pro and fails the tree-background condition. |

### What we learned against your requirements
| Requirement | Current status | Reason |
|:---|:---|:---|
| Median IoU ≥ 0.60 | Not evaluated yet | Requires human-labeled ground-truth boxes. |
| Median software latency ≤ 33 ms | Not met on M1 Pro at 1280 | Typical model inference was about 75 ms, excluding most logging/display work. |
| No loss >15 frames at 30 fps | Not met for tree scenes | The detector missed the drone through tree-background portions. |


### Experiment 1.1 — Stock YOLO Feasibility Baseline
| Category | Measurement / Result |
|:---|:---|
| Host System | M1 Pro MacBook Pro |
| Input Video | iPhone 13 Mini (4K, 60 fps) |
| Model | Ultralytics YOLOv8 Nano (`yolov8n.pt`) |
| Inference Res | 1280 pixels |
| Primary Class | `airplane` |
| Avg Latency | ~75 ms (M1 Pro) |
| Peak Latency | >100 ms |
| Sky Perf | Generally accurate; occasional `kite` classification |
| Tree Perf | Failure (Target not recognized) |
| Result | Partial Pass. Stock weights work for sky, but fail for clutter. |

### Experiment 1.2 — Visual Fidelity Deep-Dive
| Scenario | Visible (Normal) | Visible (Zoom) | Apperance |
|:---|:---|:---|:---|
| Sky Frame | Yes | Yes | Somewhat blurry |
| Tree Frame | Yes | Yes | Heavily blurred; blended contrast |

### Experiment 1.21 — Center-Crop Detection Test
| Category | Measurement / Result |
|:---|:---|
| Host System | M1 Pro MacBook Pro |
| Model | Ultralytics YOLOv8 Nano (`yolov8n.pt`) |
| Input | Center `1280 × 1280` crop from the original 4K video |
| Inference Resolution | `1280` |
| Average Inference Time | `138.1 ms` |
| Approximate Processing Rate | `7.2 fps` |
| Drone Coverage | Drone was inside the crop for most of the tested video |
| Sky / favorable performance | Drone could be detected in favorable conditions |
| Tree-background performance | Drone was still mostly not detected |
| False Positives | Propellers were sometimes labeled as `bird`; a few tree-background frames also produced `bird` detections |
| Result | Fail for the tree-background condition. Increasing effective target detail through a center crop did not yield reliable detection and substantially increased inference latency. |


### Experiment 1.3 — Background and Range Sensitivity Study
| Test ID | Approximate Range | Dominant Background | Observed Stock-YOLO Behavior | Interpretation |
|:---|:---|:---|:---|:---|
| A | 20–50 ft | Mostly sky | Drone was usually detected correctly as `airplane`; confidence was often near 0.90 while moving. Propellers were occasionally labeled as `bird`. | Favorable baseline condition. Stock YOLO is viable for initial development and measurement. |
| B | 20–50 ft; some passes at 10–20 ft | Trees | Drone was rarely identified correctly. One approximately 3–5 second segment was accurate while the drone flew away. At close range, incorrect labels included `train`, `bench`, and `bear`. | Tree-background clutter is the primary failure mode. The failure persists at short range, so limited target pixel size is not the only cause. |
| C | 50–100 ft | Mostly sky | Drone was generally detected correctly at shorter portions of the range, but detection/classification degraded approaching 100 ft. | Increasing range is a secondary failure mode due to reduced target detail and weaker visual evidence. |

### Experiment 1.4 — Representative Stock-YOLO Evaluation Manifest

> All entries are qualitative observations from the stock YOLO baseline. Exact detection accuracy will be calculated later from human-labeled ground-truth bounding boxes.

| ID | Source Video | Approximate Range | Background | Human Can See Drone? | Observed YOLO Result | Notes |
|:---|:---|:---|:---|:---|:---|:---|
| TREE-01 | `Video_2.1` | 7–10 ft | Trees | Yes | `bird` / `bear` incorrect classification | Very close target. YOLO box was concentrated around the drone/camera area rather than identifying the full drone as `airplane`. |
| TREE-02 | `Video_2.2` | 10–20 ft | Trees with some sky | Yes | Mostly missed; occasional `airplane`; incorrect `train` and `boat` labels | As range increased, some segments were classified as `airplane`, but most detections were missed or incorrectly classified. |
| TREE-03 | `Video_2.3` | 15–25 ft | Trees | Yes | Mostly missed; occasional `airplane` | Motion appeared to increase the frequency of `airplane` detections, but YOLO still missed the drone for more than half of the observed segment. |
| SKY-01  | `Video_1.1` | 10–20 ft | Sky with clouds | Yes | `airplane`; occasional `bird` near propellers | The drone was highly detailed. The model sometimes interpreted propeller features as birds. |
| SKY-02  | `Video_1.2` | 20–50 ft | Sky | Yes | Consistently `airplane` | YOLO maintained a bounding box around the drone with high apparent accuracy throughout the observed segment. |
| SKY-03  | `Video_1.3` | 40–70 ft | Sky | Yes | Consistently `airplane` | Very accurate detection at this range under sky-background conditions. |
| SKY-04  | `Video_1.4` | 20–40 ft | Sky | Yes | Consistently `airplane` | Very accurate detection under sky-background conditions. |
| SKY-05  | `Video_1.5` | 40–70 ft | Sky | Yes | Consistently `airplane` | Very accurate detection at this range under sky-background conditions. |

### Experiment 1.5 — Quantitative Detection Evaluation
| Metric | Video 1 (Sky / Long Range) | Video 2 (Trees / Clutter) |
|:---|:---|:---|
| Annotated Frames | 69 | 102 |
| Median IoU | 0.787 | 0.000|
| Success Rate (IoU >= 0.6) | 81.2% | 36.3%|
| Total Misses (IoU = 0) | 12 | 64 |
| False Classifications | `airplane`, `kite` | `airplane`, `bird`, `kite`, `bear`, `traffic light` |

### Experiment 1.6 — Detector + Kalman Filter Integration

**Test condition:** Video 2, tree/clutter background, YOLOv8n detector with a
constant-velocity Kalman filter and up to 20 predicted-only frames.

**Observed behavior:**
- The tracker maintained an accurate estimate for approximately 15–25 frames
  after temporary detector loss.
- Tracking was visually near-perfect in sky-background portions of the test.
- The tracker reduced the effect of several transient detector
  misclassifications.
- In one cluttered segment, YOLO classified a lamp as `kite`. The association
  logic attached the tracker to this false detection for approximately
  100 frames, despite valid drone detections occurring later.

**Conclusion:**
A Kalman filter improves short-gap continuity but cannot independently identify
the correct target. Robust tracking requires target-association gates that
consider motion consistency, box-size consistency, and initialization of the
intended target.

### Experiment 1.7 — Gated Association and Class Priority

**Change tested:**
- Added manual target initialization.
- Added class-aware association, prioritizing `airplane` detections over
  `kite` and `bird`.
- Tested relaxed spatial and size gates.

**Result:**
- Class priority produced a qualitative improvement over the previous gated
  version.
- Manual initialization did not materially improve acquisition or sustained
  tracking in the tree-background sequence.
- The system often lost the selected drone shortly after initialization because
  the detector did not provide a sufficiently stable drone detection against
  trees.
- Tree-background performance remains substantially weaker than sky-background
  performance.

**Engineering conclusion:**
Manual target initialization establishes initial identity but cannot compensate
for unreliable visual measurements. The system will next be evaluated as an
automatic sky-background tracker, while cluttered-background tracking is
deferred to a future custom-detector/fine-tuning phase.
