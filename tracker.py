import numpy as np
from filterpy.kalman import KalmanFilter

# Labels treated as valid drone candidates, in priority order.
# "airplane" is always preferred over "kite", "bird", etc.
PRIORITY_LABEL = "airplane"
ALLOWED_LABELS = {"airplane", "kite", "bird"}

class DroneTracker:
    def __init__(self, max_disappeared=20):
        self.kf = KalmanFilter(dim_x=4, dim_z=2)
        self.kf.F = np.array([[1, 0, 1, 0], [0, 1, 0, 1],
                               [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)
        self.kf.H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=float)
        self.kf.P *= 10.0
        self.kf.R = np.eye(2) * 5
        self.kf.Q = np.eye(4) * 0.1

        self.center = None
        self.disappeared = 0
        self.max_disappeared = max_disappeared
        self.tracked_box = None

        # Relaxed gates — wide enough not to reject fast motion
        self.max_distance_gate = 400   # pixels from KF prediction
        self.size_variance_gate = 1.5  # box size can change up to 150%

    def _state(self):
        """Return KF position as plain Python floats."""
        s = self.kf.x.flatten()
        return float(s[0]), float(s[1])

    def update(self, detections):
        """
        detections: list of (box, label) tuples
            box   = [x1, y1, x2, y2]
            label = string from YOLO names dict
        Returns tracked_box [x1, y1, x2, y2] or None.
        """
        self.kf.predict()
        pred_x, pred_y = self._state()

        # --- LABEL PRIORITY: separate airplane detections from the rest ---
        airplane_detections = [(b, l) for b, l in detections if l == PRIORITY_LABEL]
        other_detections    = [(b, l) for b, l in detections if l in ALLOWED_LABELS and l != PRIORITY_LABEL]

        # Try airplane candidates first; fall back to others only if none found
        candidate_pool = airplane_detections if airplane_detections else other_detections

        best_detection = None
        best_dist = float("inf")

        prev_w = (self.tracked_box[2] - self.tracked_box[0]) if self.tracked_box else None

        for box, label in candidate_pool:
            w  = box[2] - box[0]
            cx = (box[0] + box[2]) / 2
            cy = (box[1] + box[3]) / 2
            dist = float(np.linalg.norm([cx - pred_x, cy - pred_y]))

            # Proximity gate (only active once tracker is initialized)
            if self.center is not None and dist > self.max_distance_gate:
                continue

            # Size gate (only active once we have a reference size)
            if prev_w is not None and prev_w > 0:
                if abs(w - prev_w) / prev_w > self.size_variance_gate:
                    continue

            if dist < best_dist:
                best_dist = dist
                best_detection = box

        # --- UPDATE ---
        if best_detection is not None:
            cx = (best_detection[0] + best_detection[2]) / 2
            cy = (best_detection[1] + best_detection[3]) / 2
            self.center = np.array([cx, cy])
            self.kf.update(self.center)
            self.disappeared = 0

            w = best_detection[2] - best_detection[0]
            h = best_detection[3] - best_detection[1]
            self.tracked_box = [cx - w/2, cy - h/2, cx + w/2, cy + h/2]

        else:
            self.disappeared += 1
            if self.disappeared > self.max_disappeared:
                self.center = None
                self.tracked_box = None
                return None

            # Ghost: slide existing box using KF velocity prediction
            kx, ky = self._state()
            w = self.tracked_box[2] - self.tracked_box[0]
            h = self.tracked_box[3] - self.tracked_box[1]
            self.tracked_box = [kx - w/2, ky - h/2, kx + w/2, ky + h/2]

        return self.tracked_box