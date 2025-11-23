# VeriLight Screen-Based Embedding

This is a simplified version of VeriLight that uses a laptop screen instead of a dedicated SLM projector for data embedding.

## Overview

Instead of requiring specialized hardware (Texas Instruments DLPDLCR230NPEVM + Raspberry Pi), this version displays BPSK-encoded patterns directly on your laptop screen. The patterns can be captured when filming someone's face in front of the screen.

## Quick Start

### Basic Usage

```bash
python screen_embedding.py
```

This will:
1. Prompt you for a message (defaults to "hello world")
2. Display the BPSK-encoded pattern fullscreen
3. The pattern continuously loops and can be captured in video

Press 'q' to quit the display.

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

### Recording Video with Embedding

1. **Start the screen embedding:**
   ```bash
   python screen_embedding.py
   ```

2. **Position the subject:**
   - Place the person in front of the laptop screen
   - The screen pattern will illuminate their face
   - Ensure good framing for facial capture

3. **Record video:**
   - Use the same camera setup as normal VeriLight
   - Record the person's face with the screen pattern visible in the background/lighting
   - The encoded data is embedded through the light reflecting off their face

4. **Verify (using existing VeriLight tools):**
   - The recorded video can be processed with VeriLight's verification pipeline
   - Extract and decode the embedded "hello world" message

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

## Future Enhancements

Possible improvements:
- Integration with existing VeriLight verification pipeline
- Adjustable brightness/colors for different lighting conditions
- Multi-screen support for higher data rates
- Real-time encoding of longer messages
- Webcam preview to show what will be captured

## Notes

- The screen-based approach is more visible than the hardware SLM version
- Best used in darker environments where the screen provides significant illumination
- May require longer exposure times or higher ISO on the camera
- The patterns are more noticeable than imperceptible hardware embedding
