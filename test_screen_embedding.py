"""
Test script for screen embedding functionality.
Tests encoding logic without requiring a display.
"""
import sys
sys.path.insert(0, '/home/user/VeriLight')

from screen_embedding import text_to_binary, create_bpsk_frames, ScreenEmbedder
from screen_embedding import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, BUFFER_SPACE,
    FREQUENCY, EMBEDDING_DURATION, NUM_INFO_CELLS, MAX_CELLS_H, MAX_CELLS_W
)


def test_text_to_binary():
    """Test text to binary conversion."""
    print("Testing text_to_binary()...")

    # Test "hello world"
    text = "hello world"
    binary = text_to_binary(text)

    # Each character should be 8 bits
    expected_length = len(text) * 8
    assert len(binary) == expected_length, f"Expected {expected_length} bits, got {len(binary)}"

    # Check first character 'h' = 104 = 01101000
    assert binary[:8] == '01101000', f"Expected 01101000, got {binary[:8]}"

    print(f"✓ Text '{text}' → {len(binary)} bits")
    print(f"  First 8 bits ('{text[0]}'): {binary[:8]}")
    return True


def test_frame_creation():
    """Test BPSK frame creation."""
    print("\nTesting create_bpsk_frames()...")

    message = "hi"
    bitstring = text_to_binary(message)
    frames = create_bpsk_frames(bitstring)

    # Check we got the right number of frames
    expected_frames = int(EMBEDDING_DURATION * FREQUENCY * 2)
    assert len(frames) == expected_frames, f"Expected {expected_frames} frames, got {len(frames)}"

    # Check frame dimensions
    for i, frame in enumerate(frames):
        assert frame.shape == (SCREEN_HEIGHT, SCREEN_WIDTH, 3), \
            f"Frame {i} has wrong shape: {frame.shape}"

    print(f"✓ Created {len(frames)} frames")
    print(f"  Frame shape: {frames[0].shape}")
    print(f"  Frame dtype: {frames[0].dtype}")

    # Check that frames alternate (some pixels should differ between consecutive frames)
    frame0_sum = frames[0].sum()
    frame1_sum = frames[1].sum()
    assert frame0_sum != frame1_sum, "Consecutive frames should differ (BPSK encoding)"
    print(f"  Frame 0 intensity sum: {frame0_sum}")
    print(f"  Frame 1 intensity sum: {frame1_sum}")

    return True


def test_embedder_creation():
    """Test ScreenEmbedder initialization."""
    print("\nTesting ScreenEmbedder()...")

    message = "test"
    embedder = ScreenEmbedder(message)

    assert embedder.message == message
    assert len(embedder.bitstring) == len(message) * 8
    assert len(embedder.frames) > 0
    assert embedder.fps == FREQUENCY * 2

    print(f"✓ ScreenEmbedder initialized")
    print(f"  Message: '{embedder.message}'")
    print(f"  Binary length: {len(embedder.bitstring)} bits")
    print(f"  Number of frames: {len(embedder.frames)}")
    print(f"  FPS: {embedder.fps}")

    return True


def test_system_parameters():
    """Display system parameters."""
    print("\nSystem Parameters:")
    print(f"  Screen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"  Cell size: {CELL_SIZE} pixels")
    print(f"  Buffer space: {BUFFER_SPACE} pixels")
    print(f"  Grid: {MAX_CELLS_H}x{MAX_CELLS_W} cells")
    print(f"  Info cells: {NUM_INFO_CELLS}")
    print(f"  Frequency: {FREQUENCY} Hz")
    print(f"  Embedding duration: {EMBEDDING_DURATION} seconds")

    # Calculate bit capacity
    bits_per_cell = int(EMBEDDING_DURATION * FREQUENCY)
    total_bits = NUM_INFO_CELLS * bits_per_cell
    total_chars = total_bits // 8

    print(f"\nCapacity:")
    print(f"  Bits per cell: {bits_per_cell}")
    print(f"  Total bits: {total_bits}")
    print(f"  Total characters: {total_chars}")

    return True


def main():
    """Run all tests."""
    print("="*60)
    print("VeriLight Screen Embedding - Unit Tests")
    print("="*60)

    tests = [
        test_system_parameters,
        test_text_to_binary,
        test_frame_creation,
        test_embedder_creation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed: {test.__name__}")
            print(f"  Error: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
