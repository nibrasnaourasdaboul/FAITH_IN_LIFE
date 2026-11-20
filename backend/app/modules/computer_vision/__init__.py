"""Computer-vision boundary for remote exercise tracking.

Planned libraries: mediapipe, opencv-python.
This package stays inert until the AI phase is explicitly approved.
"""


class PoseTrackingService:
    """Future home for pose landmarks, joint angles, and rep counting."""

    # مكان مخصص لاحقاً لتحليل إطار حركة المريض.
    def analyze_frame(self, frame_bytes: bytes) -> dict:
        raise NotImplementedError("Computer vision is not enabled yet.")
