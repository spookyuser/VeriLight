"""
Test camera availability for screen embedding recording.
"""
import cv2
import sys


def test_camera_detection():
    """Test if we can detect and open cameras."""
    print("Testing camera detection...")
    print("-" * 60)

    available = []

    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)

                print(f"✓ Camera {i} detected:")
                print(f"  Resolution: {width}x{height}")
                print(f"  FPS: {fps}")
                print(f"  Frame shape: {frame.shape}")
                available.append(i)
            cap.release()

    if not available:
        print("✗ No cameras detected")
        print("\nNote: In a headless environment, this is expected.")
        print("On a laptop with a webcam, you should see at least one camera.")
        return False

    print("-" * 60)
    print(f"Found {len(available)} camera(s): {available}")
    return True


def test_video_writer():
    """Test if we can create a video writer."""
    print("\nTesting video writer...")
    print("-" * 60)

    try:
        import tempfile
        import os

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            temp_path = tmp.name

        # Try to create a video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(temp_path, fourcc, 25.0, (640, 480))

        if writer.isOpened():
            print("✓ Video writer initialized successfully")

            # Write a test frame
            test_frame = cv2.imread('/dev/null')  # This will be None
            if test_frame is None:
                # Create a dummy frame
                test_frame = (255 * cv2.randn((480, 640, 3), 0.5, 0.2)).astype('uint8')

            writer.write(test_frame)
            writer.release()

            # Check if file was created
            if os.path.exists(temp_path):
                size = os.path.getsize(temp_path)
                print(f"✓ Test video file created: {size} bytes")
                os.remove(temp_path)
                return True
            else:
                print("✗ Video file was not created")
                return False
        else:
            print("✗ Could not initialize video writer")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all camera tests."""
    print("="*60)
    print("Camera System Test")
    print("="*60)
    print()

    results = {
        'camera_detection': test_camera_detection(),
        'video_writer': test_video_writer(),
    }

    print("\n" + "="*60)
    print("Results:")
    print("-"*60)

    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test.replace('_', ' ').title()}: {status}")

    print("="*60)

    all_passed = all(results.values())

    if not all_passed:
        print("\nNote: Some tests may fail in headless/containerized environments.")
        print("This is expected if you're running without a physical camera.")
        print("The recording feature will work on a laptop with a webcam.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
