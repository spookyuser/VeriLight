# VeriLight Screen-Based Embedding

This is a simplified version of VeriLight that uses a laptop screen instead of a dedicated SLM projector for data embedding.

## Overview

Instead of requiring specialized hardware (Texas Instruments DLPDLCR230NPEVM + Raspberry Pi), this version displays BPSK-encoded patterns directly on your laptop screen. The patterns can be captured when filming someone's face in front of the screen.

## Quick Start

### Display Only (No Recording)

```bash
python screen_embedding.py
```

This will:
1. Prompt you for a message (defaults to "hello world")
2. Display the BPSK-encoded pattern fullscreen
3. The pattern continuously loops and can be captured in video

Press 'q' to quit the display.

### Display + Recording (Recommended)

```bash
python screen_embedding_record.py
```

This will:
1. Prompt you for a message (defaults to "hello world")
2. Detect available cameras and let you select one
3. Display the BPSK pattern fullscreen
4. Show a webcam preview window
5. Let you record video with the pattern embedded

**Controls:**
- **SPACE** - Start/stop recording
- **Q** - Quit

Recordings are saved to the `recordings/` directory as MP4 files.

## How It Works

### BPSK Encoding
The system uses Binary Phase Shift Keying (BPSK) to encode data:
- **Bit 0**: Cell blinks during even phase (frames 0, 2, 4, ...)
- **Bit 1**: Cell blinks during odd phase (frames 1, 3, 5, ...)

### Grid Layout
The screen is divided into a grid of cells:
- **Border cells** (outer edge): Provide synchronization, blink at base frequency
- **Corner markers** (2x2 blocks): Help with localization and alignment
- **Info cells** (interior): Encode the actual message data

### Parameters
- **Cell size**: 40 pixels (configurable)
- **Frequency**: 3 Hz (cells complete one on/off cycle every 333ms)
- **Embedding duration**: 4 seconds per message loop
- **Grid**: Automatically calculated based on screen resolution

## Example Workflow

### Complete Recording Session

1. **Start the recording system:**
   ```bash
   python screen_embedding_record.py
   ```

2. **Configure settings:**
   - Enter your message (e.g., "hello world")
   - Select camera if multiple are available
   - Choose output directory (default: `recordings/`)

3. **Position yourself:**
   - Sit in front of the laptop screen
   - Make sure your face is visible in the preview window
   - The screen pattern will illuminate your face
   - Darker room = better embedding visibility

4. **Record:**
   - Press **SPACE** to start recording
   - Speak or move naturally for 10-30 seconds
   - The red "REC" indicator shows recording is active
   - Press **SPACE** again to stop recording
   - Video is automatically saved with timestamp

5. **Verify (using existing VeriLight tools):**
   - Find your video in `recordings/recording_YYYYMMDD_HHMMSS.mp4`
   - Process with VeriLight's verification pipeline to extract the embedded message
   - The "hello world" message should be recoverable from the facial video

### Tips for Best Results

- **Lighting**: Use a darker environment so the screen pattern is more prominent
- **Distance**: Sit 2-3 feet from the screen for optimal illumination
- **Duration**: Record at least 10-15 seconds to capture multiple embedding cycles
- **Movement**: Natural head movements are fine, but stay generally centered
- **Camera**: Built-in laptop webcam works, but external camera may give better quality

## Comparison with Hardware VeriLight

| Feature | Screen-Based | Hardware (SLM) |
|---------|-------------|----------------|
| **Setup** | Just a laptop | Requires SLM + Raspberry Pi + Camera |
| **Portability** | Very portable | Bulky hardware setup |
| **Cost** | Free (uses existing laptop) | ~$500+ for SLM hardware |
| **Brightness** | Limited by laptop screen | Very bright, adjustable |
| **Imperceptibility** | More visible patterns | Can be nearly imperceptible |
| **Adaptation** | Fixed brightness | Real-time adaptive brightness |

## Customization

You can modify the following parameters in `screen_embedding.py`:

```python
CELL_SIZE = 40          # Size of each cell in pixels
FREQUENCY = 3           # Blinking frequency in Hz
EMBEDDING_DURATION = 4  # Duration of one message loop
CELL_COLOR = [250, 150, 100]  # BGR color values
```

## Technical Details

### Message Encoding Process
1. Text → Binary (ASCII encoding, 8 bits per character)
2. Binary → Padded to fill available info cells
3. BPSK encoding creates frame sequence
4. Frames displayed in continuous loop

### Bit Capacity
The number of bits you can embed depends on:
- Screen resolution (determines grid size)
- Cell size + buffer space
- Embedding duration
- Frequency

For a typical 1920x1080 screen:
- Grid: ~28 x 16 cells
- Info cells: ~380 (after removing borders and corners)
- Bits per cell: 12 (4 seconds × 3 Hz)
- **Total capacity: ~4,560 bits (~570 characters)**

## Testing Your Setup

Before recording a full session, verify everything works:

```bash
# Test camera detection
python test_camera.py

# Test encoding without display (unit tests)
python test_screen_embedding.py
```

## File Overview

- **screen_embedding.py** - Display only (no recording)
- **screen_embedding_record.py** - Display + webcam recording ⭐ (recommended)
- **test_screen_embedding.py** - Unit tests for encoding logic
- **test_camera.py** - Test camera availability
- **SCREEN_EMBEDDING.md** - This documentation

## Future Enhancements

Possible improvements:
- ✅ ~~Webcam preview and recording~~ (implemented!)
- Integration with existing VeriLight verification pipeline
- Adjustable brightness/colors for different lighting conditions
- Multi-screen support for higher data rates
- Real-time encoding of longer messages
- Auto-detection of optimal screen brightness
- Integration with facial feature extraction pipeline

## Notes

- The screen-based approach is more visible than the hardware SLM version
- Best used in darker environments where the screen provides significant illumination
- May require longer exposure times or higher ISO on the camera
- The patterns are more noticeable than imperceptible hardware embedding
