"""
Screen-based data embedding for VeriLight.
Uses laptop screen instead of SLM projector to embed data.

This simplified version embeds "hello world" using BPSK encoding
displayed on a laptop screen.

Usage: python screen_embedding.py
"""
import numpy as np
import cv2
import time
from threading import Thread, Event

# Simplified config for screen-based embedding
SCREEN_WIDTH = 1920  # Can be adjusted based on your screen
SCREEN_HEIGHT = 1080
CELL_SIZE = 40  # Larger cells for screen visibility
BUFFER_SPACE = 15
FREQUENCY = 3  # Hz - cells blink at this frequency
EMBEDDING_DURATION = 4  # seconds per loop
LOCALIZATION_N = 2  # 2x2 corner markers

# Calculate grid dimensions
MAX_CELLS_W = int(SCREEN_WIDTH / (CELL_SIZE + BUFFER_SPACE))
MAX_CELLS_H = int(SCREEN_HEIGHT / (CELL_SIZE + BUFFER_SPACE))

# Calculate number of info cells (excluding border/pilot cells and corner markers)
NUM_PILOT_CELLS = MAX_CELLS_W * 2 + MAX_CELLS_H * 2 - 4 - ((2 * LOCALIZATION_N - 1) * 4)
NUM_INFO_CELLS = (MAX_CELLS_H * MAX_CELLS_W) - NUM_PILOT_CELLS - 4 * (LOCALIZATION_N ** 2)

# Color settings (BGR format for OpenCV)
CELL_COLOR = [250, 150, 100]  # Light blue/cyan - visible but not too bright
CORNER_COLOR = [100, 255, 100]  # Light green for corner markers
BACKGROUND_COLOR = [0, 0, 0]  # Black background


def text_to_binary(text):
    """Convert text to binary string."""
    binary = ''.join(format(ord(char), '08b') for char in text)
    return binary


def overall_cell_to_row_col(cell_num):
    """Convert overall cell number to row, column coordinates."""
    row = cell_num // MAX_CELLS_W
    col = cell_num % MAX_CELLS_W
    return row, col


def create_bpsk_frames(bitstring):
    """
    Create BPSK-encoded frames for screen display.

    BPSK encoding:
    - Bit 0: Cell blinks during even phase (frames 0, 2, 4, ...)
    - Bit 1: Cell blinks during odd phase (frames 1, 3, 5, ...)

    Args:
        bitstring: Binary string to encode

    Returns:
        List of frames (numpy arrays) to display
    """
    # Calculate bits per cell and pad bitstring if needed
    max_bits_per_cell = int(EMBEDDING_DURATION * FREQUENCY)
    max_total_bits = NUM_INFO_CELLS * max_bits_per_cell

    # Pad or truncate bitstring
    if len(bitstring) < max_total_bits:
        bitstring = bitstring + '0' * (max_total_bits - len(bitstring))
    else:
        bitstring = bitstring[:max_total_bits]

    # Number of frames to create (2 frames per bit period)
    num_frames = int(EMBEDDING_DURATION * FREQUENCY * 2)

    frames = []

    for frame_idx in range(num_frames):
        # Create empty frame
        frame = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)

        # Determine if this is an even or odd phase
        is_even_phase = (frame_idx % 2) == 0

        # Determine if corner markers should be on (blink at same frequency)
        corner_on = is_even_phase

        info_cell_num = 0

        # Process each cell in the grid
        for overall_cell_num in range(MAX_CELLS_W * MAX_CELLS_H):
            r, c = overall_cell_to_row_col(overall_cell_num)

            # Skip if this would be a corner marker location
            if LOCALIZATION_N and (
                (r < LOCALIZATION_N and c < LOCALIZATION_N) or  # Top-left
                (r < LOCALIZATION_N and c >= MAX_CELLS_W - LOCALIZATION_N) or  # Top-right
                (r >= MAX_CELLS_H - LOCALIZATION_N and c < LOCALIZATION_N) or  # Bottom-left
                (r >= MAX_CELLS_H - LOCALIZATION_N and c >= MAX_CELLS_W - LOCALIZATION_N)  # Bottom-right
            ):
                continue

            # Calculate cell position in pixels
            cell_top = r * (CELL_SIZE + BUFFER_SPACE)
            cell_bottom = cell_top + CELL_SIZE
            cell_left = c * (CELL_SIZE + BUFFER_SPACE)
            cell_right = cell_left + CELL_SIZE

            # Check bounds
            if cell_bottom > SCREEN_HEIGHT or cell_right > SCREEN_WIDTH:
                continue

            # Border/pilot cells (always blink at base frequency for sync)
            if r == 0 or r == MAX_CELLS_H - 1 or c == 0 or c == MAX_CELLS_W - 1:
                if is_even_phase:
                    frame[cell_top:cell_bottom, cell_left:cell_right] = CELL_COLOR
            else:
                # Info cell - encode data
                if info_cell_num < NUM_INFO_CELLS:
                    bit_index = int(frame_idx / 2)  # Which bit we're encoding
                    cell_start_bit = info_cell_num * max_bits_per_cell

                    if bit_index < max_bits_per_cell and cell_start_bit + bit_index < len(bitstring):
                        bit = bitstring[cell_start_bit + bit_index]

                        # BPSK: 0 = blink on even phase, 1 = blink on odd phase
                        if (bit == '0' and is_even_phase) or (bit == '1' and not is_even_phase):
                            frame[cell_top:cell_bottom, cell_left:cell_right] = CELL_COLOR

                    info_cell_num += 1

        # Add corner markers
        if corner_on and LOCALIZATION_N:
            marker_size = LOCALIZATION_N * (CELL_SIZE + BUFFER_SPACE) - BUFFER_SPACE

            # Top-left
            frame[0:marker_size, 0:marker_size] = CORNER_COLOR
            # Top-right
            right_start = (MAX_CELLS_W - LOCALIZATION_N) * (CELL_SIZE + BUFFER_SPACE)
            frame[0:marker_size, right_start:right_start + marker_size] = CORNER_COLOR
            # Bottom-left
            bottom_start = (MAX_CELLS_H - LOCALIZATION_N) * (CELL_SIZE + BUFFER_SPACE)
            frame[bottom_start:bottom_start + marker_size, 0:marker_size] = CORNER_COLOR
            # Bottom-right
            frame[bottom_start:bottom_start + marker_size, right_start:right_start + marker_size] = CORNER_COLOR

        frames.append(frame)

    return frames


class ScreenEmbedder:
    """Handles displaying BPSK frames on the laptop screen."""

    def __init__(self, message="hello world"):
        self.message = message
        self.bitstring = text_to_binary(message)
        self.frames = create_bpsk_frames(self.bitstring)
        self.stop_event = Event()
        self.fps = FREQUENCY * 2  # 2 frames per cycle
        self.frame_interval = 1.0 / self.fps

    def display_loop(self):
        """Main display loop - shows frames in sequence."""
        window_name = "VeriLight Screen Embedding"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        print(f"\n{'='*60}")
        print(f"VeriLight Screen Embedding")
        print(f"{'='*60}")
        print(f"Message: '{self.message}'")
        print(f"Binary length: {len(self.bitstring)} bits")
        print(f"Grid: {MAX_CELLS_H}x{MAX_CELLS_W} cells")
        print(f"Info cells: {NUM_INFO_CELLS}")
        print(f"Frames: {len(self.frames)}")
        print(f"FPS: {self.fps}")
        print(f"\nDisplaying on screen... Press 'q' to quit")
        print(f"{'='*60}\n")

        frame_idx = 0
        last_frame_time = time.time()

        while not self.stop_event.is_set():
            current_time = time.time()

            # Display frame if enough time has passed
            if current_time - last_frame_time >= self.frame_interval:
                frame = self.frames[frame_idx]
                cv2.imshow(window_name, frame)

                frame_idx = (frame_idx + 1) % len(self.frames)
                last_frame_time = current_time

            # Check for quit key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nStopping display...")
                break

        cv2.destroyAllWindows()

    def start(self):
        """Start displaying frames."""
        self.display_loop()

    def stop(self):
        """Stop displaying frames."""
        self.stop_event.set()


def main():
    """Main entry point for screen embedding demo."""
    print("\n" + "="*60)
    print("VeriLight Screen-Based Embedding Demo")
    print("="*60)
    print("\nThis demo displays a BPSK-encoded 'hello world' message")
    print("on your laptop screen. The pattern can be captured in video")
    print("of someone's face when they are in front of the screen.")
    print("\nThe embedding uses blinking cells to encode binary data:")
    print("- Border cells provide synchronization")
    print("- Corner markers help with localization")
    print("- Interior cells encode the actual message")
    print("\n" + "="*60)

    # Allow user to customize message
    custom_message = input("\nEnter message to embed (or press Enter for 'hello world'): ").strip()
    if not custom_message:
        custom_message = "hello world"

    print(f"\nPreparing to embed: '{custom_message}'")
    print("The screen will go fullscreen. Press 'q' to exit.")
    print("\nStarting in 3 seconds...")
    time.sleep(3)

    # Create and start embedder
    embedder = ScreenEmbedder(custom_message)
    try:
        embedder.start()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        embedder.stop()

    print("\nDemo completed!")


if __name__ == "__main__":
    main()
