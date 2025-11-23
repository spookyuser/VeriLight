"""
Screen-based data embedding with simultaneous video recording.
Displays BPSK pattern on screen while recording webcam video.

Usage: python screen_embedding_record.py
"""
import numpy as np
import cv2
import time
import os
from datetime import datetime
from threading import Thread, Event
import sys

# Import from the base screen_embedding module
sys.path.insert(0, '/home/user/VeriLight')
from screen_embedding import (
    text_to_binary, create_bpsk_frames,
    SCREEN_WIDTH, SCREEN_HEIGHT, FREQUENCY
)


class ScreenEmbedderWithRecording:
    """Displays BPSK frames on screen while recording video from webcam."""

    def __init__(self, message="hello world", camera_id=0, output_dir="recordings"):
        self.message = message
        self.bitstring = text_to_binary(message)
        self.frames = create_bpsk_frames(self.bitstring)
        self.camera_id = camera_id
        self.output_dir = output_dir

        self.stop_event = Event()
        self.recording = False
        self.fps = FREQUENCY * 2
        self.frame_interval = 1.0 / self.fps

        # Video writer settings
        self.video_writer = None
        self.video_path = None

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

    def initialize_camera(self):
        """Initialize the webcam."""
        print(f"Initializing camera {self.camera_id}...")
        cap = cv2.VideoCapture(self.camera_id)

        if not cap.isOpened():
            print(f"ERROR: Could not open camera {self.camera_id}")
            return None

        # Set camera properties for better quality
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 25)

        # Get actual properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        print(f"Camera initialized: {width}x{height} @ {fps} FPS")
        return cap

    def start_recording(self, cap):
        """Start recording video."""
        if self.recording:
            return

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_path = os.path.join(
            self.output_dir,
            f"recording_{timestamp}.mp4"
        )

        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            self.video_path,
            fourcc,
            25.0,  # Record at 25 FPS
            (width, height)
        )

        if not self.video_writer.isOpened():
            print("ERROR: Could not initialize video writer")
            return

        self.recording = True
        print(f"\n{'='*60}")
        print(f"📹 RECORDING STARTED")
        print(f"Output: {self.video_path}")
        print(f"{'='*60}\n")

    def stop_recording(self):
        """Stop recording video."""
        if not self.recording:
            return

        self.recording = False
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

        print(f"\n{'='*60}")
        print(f"⏹ RECORDING STOPPED")
        print(f"Saved: {self.video_path}")
        print(f"{'='*60}\n")

    def run(self):
        """Main loop - displays pattern and records video."""
        # Initialize camera
        cap = self.initialize_camera()
        if cap is None:
            print("Failed to initialize camera. Exiting.")
            return

        # Create windows
        embedding_window = "VeriLight Embedding Pattern"
        preview_window = "Camera Preview (Press SPACE to record, Q to quit)"

        cv2.namedWindow(embedding_window, cv2.WINDOW_NORMAL)
        cv2.namedWindow(preview_window, cv2.WINDOW_NORMAL)

        # Make embedding window fullscreen
        cv2.setWindowProperty(
            embedding_window,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN
        )

        # Position preview window
        cv2.moveWindow(preview_window, 100, 100)
        cv2.resizeWindow(preview_window, 640, 480)

        print(f"\n{'='*60}")
        print(f"VeriLight Screen Embedding with Recording")
        print(f"{'='*60}")
        print(f"Message: '{self.message}'")
        print(f"Binary length: {len(self.bitstring)} bits")
        print(f"Frames: {len(self.frames)}")
        print(f"Display FPS: {self.fps}")
        print(f"\nControls:")
        print(f"  SPACE - Start/Stop recording")
        print(f"  Q     - Quit")
        print(f"{'='*60}\n")

        frame_idx = 0
        last_frame_time = time.time()
        frame_count = 0

        try:
            while not self.stop_event.is_set():
                current_time = time.time()

                # Display embedding frame if enough time has passed
                if current_time - last_frame_time >= self.frame_interval:
                    embedding_frame = self.frames[frame_idx]
                    cv2.imshow(embedding_window, embedding_frame)

                    frame_idx = (frame_idx + 1) % len(self.frames)
                    last_frame_time = current_time

                # Capture and display camera frame
                ret, camera_frame = cap.read()
                if ret:
                    # Create preview frame with recording indicator
                    preview_frame = camera_frame.copy()

                    # Add recording indicator
                    if self.recording:
                        # Red dot in corner
                        cv2.circle(preview_frame, (30, 30), 15, (0, 0, 255), -1)
                        cv2.putText(
                            preview_frame,
                            "REC",
                            (55, 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2
                        )

                        # Frame counter
                        cv2.putText(
                            preview_frame,
                            f"Frame: {frame_count}",
                            (preview_frame.shape[1] - 150, 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2
                        )
                        frame_count += 1
                    else:
                        # Show instructions
                        cv2.putText(
                            preview_frame,
                            "Press SPACE to start recording",
                            (10, preview_frame.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            2
                        )

                    cv2.imshow(preview_window, preview_frame)

                    # Write frame if recording
                    if self.recording and self.video_writer:
                        self.video_writer.write(camera_frame)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    print("\nQuitting...")
                    break
                elif key == ord(' '):  # Space bar
                    if self.recording:
                        self.stop_recording()
                        frame_count = 0
                    else:
                        self.start_recording(cap)

        except KeyboardInterrupt:
            print("\nInterrupted by user")
        finally:
            # Cleanup
            if self.recording:
                self.stop_recording()

            cap.release()
            cv2.destroyAllWindows()

    def start(self):
        """Start the embedding and recording system."""
        self.run()

    def stop(self):
        """Stop the system."""
        self.stop_event.set()


def list_cameras():
    """Find available cameras."""
    print("Searching for cameras...")
    available = []

    for i in range(10):  # Check first 10 camera indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available.append(i)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                print(f"  Camera {i}: {width}x{height}")
            cap.release()

    return available


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("VeriLight Screen Embedding with Recording")
    print("="*60)
    print("\nThis will:")
    print("1. Display a BPSK-encoded pattern on your screen")
    print("2. Show a webcam preview window")
    print("3. Let you record video while the pattern is displayed")
    print("\n" + "="*60)

    # Find cameras
    cameras = list_cameras()

    if not cameras:
        print("\nERROR: No cameras found!")
        print("Make sure a webcam is connected and accessible.")
        return

    # Select camera
    if len(cameras) == 1:
        camera_id = cameras[0]
        print(f"\nUsing camera {camera_id}")
    else:
        print(f"\nAvailable cameras: {cameras}")
        try:
            camera_id = int(input(f"Select camera ID (default: {cameras[0]}): ") or cameras[0])
            if camera_id not in cameras:
                print(f"Invalid camera ID. Using {cameras[0]}")
                camera_id = cameras[0]
        except ValueError:
            camera_id = cameras[0]

    # Get message to embed
    custom_message = input("\nEnter message to embed (or press Enter for 'hello world'): ").strip()
    if not custom_message:
        custom_message = "hello world"

    # Get output directory
    output_dir = input("\nOutput directory (default: recordings): ").strip()
    if not output_dir:
        output_dir = "recordings"

    print(f"\nMessage: '{custom_message}'")
    print(f"Camera: {camera_id}")
    print(f"Output: {output_dir}/")
    print("\nStarting in 3 seconds...")
    print("Position yourself in front of the screen!")
    time.sleep(3)

    # Create and run embedder
    embedder = ScreenEmbedderWithRecording(
        message=custom_message,
        camera_id=camera_id,
        output_dir=output_dir
    )

    try:
        embedder.start()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        embedder.stop()

    print("\nDone! Check your recordings in the output directory.")


if __name__ == "__main__":
    main()
