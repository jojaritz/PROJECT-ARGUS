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

       Category	                        Current plan
Primary workstation	          |  Windows 11 desktop with NVIDIA RTX 2080
Mobile/development system     |  MacBook Pro with M1 Pro
Primary live-camera candidate	|  Sony FDR-AX33 camcorder
Secondary live-camera         |	 Canon EOS R50 with RF-S 18–45 mm lens
candidate          
Baseline data camera          |	 iPhone 13 Mini main camera
Initial test target           |	 DJI Mini 2 SE, stock configuration
Planned live-video interface	|  USB 3 HDMI capture device, pending acquisition and acceptance testing
Development environment       |	 Python, VS Code, OpenCV, NumPy, PyTorch/Ultralytics YOLO
Initial input data	          |  iPhone 13 Mini video recorded at 3840×2160, 60 fps


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

    Measurement	              Result
Host system	      |  M1 Pro MacBook Pro
Source camera	    |  iPhone 13 Mini main camera
Video dimensions  |	 3840 × 2160
Source frame rate	|  60.00 fps
Total video frames|  2,075
Full preview-loop |  39.16 fps
throughput
Observed decode + |  Typically 9–10 ms; occasional peaks near 14 ms
resize time	
Drone visibility	|  Visually identifiable throughout the baseline clip
Farthest observed |  Approximately 56 × 26 pixels at 4K
target footprint	


Initial Finding: Small-Target Detection Risk
At the farthest point, the drone is approximately 56 × 26 pixels in a 4K frame. Resizing the full 3840-pixel-wide frame to YOLO’s common 640-pixel-wide input would reduce the drone to roughly 9 × 4 pixels.

This is likely insufficient for reliable stock-model detection. Phase 1 must evaluate detector input resolution, cropping, and tiled inference rather than assuming default 640 × 640 inference is appropriate.


## 6. Performance Targets — Version 0.1

ID	  |Metric	      |Initial requirement	    |Measurement definition
-----------------------------------------------------------------
 PERF-|Localization | Median IoU ≥ 0.60      |Compare the estimated drone bounding box with a human-labeled 
 01   |accuracy     |                        |ground-truth bounding box on frames where the drone is visible.
 ----------------------------------------------------------------
 PERF-|Software     |Median                  |Measure software processing time from frame ingestion to the tracker producing its state estimate. 
 02   |pipeline     |frame-arrival-to-tracker|Camera and capture-device delay are excluded until live testing begins.
      |latency      |output time ≤ 33 ms     |
 ----------------------------------------------------------------
 PERF-|Target       |No loss longer than 15  |During defined test conditions, the system must not lack both an accepted detector 
 03   |continuity   |consec. frames-30 fps   |measurement and a valid tracker estimate for more than approximately 0.5 seconds.


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

ID	  |Risk              |Category   |Why it matters                              |  Initial mitigation
---------------------------------------------------------------------------------------------------------------------
 PERF-|The drone becomes | Technical |At the farthest point in the baseline video,| Measure detection performance at multiple input resolutions; 
 01   |too small for     |           |the target is only about 56 × 26 pixels at  | evaluate cropped or tiled inference; establish a measured maximum 
      |reliable detection|           |4K. Full-frame downscaling can reduce it    | operating range.
      | at longer ranges.|           |below detectable size.                      | 
 --------------------------------------------------------------------------------------------------------------------
 PERF-|Trees, houses,    |Technical  |The background can resemble or obscure the  |Record test metadata; evaluate separately for clear sky, cluttered 
 02   |clouds, lighting  |envirnmt.  |drone, reducing accuracy and continuity.    |background, directional motion, and occlusion; use a tracker to 
      |changes, and      |           |                                            |bridge brief missed detections.
      |occlusion cause   |           |                                            |
      |false detections  |           |                                            |
      |or target loss.   |           |                                            |
 ---------------------------------------------------------------------------------------------------------------------
 PERF-|Capture,decoding, |Technical  |A delayed target estimate becomes less      |Timestamp each module boundary; profile offline processing first; 
      |tracking, display,|integration|camera pointing.                            |later measure capture-to-output latency with live hardware; 
 03   |inference,        |           |useful for real-time observation and later  |process the newest frame rather than queueing old frames.
      |or logging creates|           |                                            |
      |excessive latency.|           |                                            |
 ----------------------------------------------------------------------------------------------------------------------
 PERF-|Stock YOLO weights|Technical  |A general-purpose detector may not have     |Establish a stock-model baseline; label a representative dataset 
 04   |do not recognize  |model      |enough examples of a small DJI Mini 2 SE    |if needed; compare model, image-resolution, and training 
      |the drone reliably|           |against varied sky and ground backgrounds.  |approaches using the same evaluation clips.
 ----------------------------------------------------------------------------------------------------------------------
 PERF-|Live HDMI capture | Hardware  |Offline video success does not prove        |Conduct a capture-card acceptance test: verify recognition, 
 05   |is unstable,      |integration|live-camera performance.                    |resolution, frame rate, stability for 10 minutes, disconnects, 
      |limited to a lower|           |                                            |freezes, and measured delay.
      |frame rate, or    |           |                                            |
      |adds a large delay|           |                                            |


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
