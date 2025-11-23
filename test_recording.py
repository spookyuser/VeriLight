"""
Simple test script to verify screen-based embedding recordings.

This creates a visual test to check if the BPSK pattern is visible
in the recorded video. For full verification with message extraction,
use VeriLight's verify.py pipeline.

Usage: python test_recording.py <video_path>
"""
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
import sys
import os


def analyze_video_for_pattern(video_path, sample_duration=5):
    """
    Analyze video to detect if BPSK pattern is visible.

    Args:
        video_path: Path to the recorded video
        sample_duration: Duration in seconds to analyze

    Returns:
        dict with analysis results
    """
    print(f"Analyzing video: {video_path}")
    print("=" * 60)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("ERROR: Cannot open video file")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    print(f"Video properties:")
    print(f"  FPS: {fps}")
    print(f"  Total frames: {total_frames}")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    print()

    # Read frames for analysis
    frames_to_read = min(int(sample_duration * fps), total_frames)
    print(f"Reading {frames_to_read} frames for analysis...")

    brightness_values = []
    frame_count = 0

    while frame_count < frames_to_read:
        ret, frame = cap.read()
        if not ret:
            break

        # Calculate average brightness
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        brightness_values.append(avg_brightness)

        frame_count += 1

    cap.release()

    if len(brightness_values) < 10:
        print("ERROR: Not enough frames read")
        return None

    brightness_values = np.array(brightness_values)

    # Analyze brightness signal for periodic patterns
    print("\nAnalyzing brightness variations...")

    # Compute FFT
    N = len(brightness_values)
    yf = fft(brightness_values - np.mean(brightness_values))  # Remove DC component
    xf = fftfreq(N, 1/fps)[:N//2]
    power = 2.0/N * np.abs(yf[0:N//2])

    # Find peaks in frequency domain
    peaks, properties = find_peaks(power, height=power.max() * 0.1, distance=5)

    # Expected embedding frequency is 3 Hz
    expected_freq = 3.0
    freq_tolerance = 1.0

    print(f"\nFrequency analysis:")
    print(f"  Expected pattern frequency: {expected_freq} Hz")
    print(f"  Looking for peaks near {expected_freq}±{freq_tolerance} Hz")

    pattern_detected = False
    detected_freq = None

    if len(peaks) > 0:
        print(f"\n  Top frequency peaks detected:")
        for i, peak_idx in enumerate(peaks[:5]):
            freq = xf[peak_idx]
            amplitude = power[peak_idx]
            print(f"    {i+1}. {freq:.2f} Hz (amplitude: {amplitude:.2f})")

            # Check if this peak is near expected frequency
            if abs(freq - expected_freq) < freq_tolerance:
                pattern_detected = True
                detected_freq = freq

    if pattern_detected:
        print(f"\n✅ PATTERN DETECTED!")
        print(f"   Found frequency peak at {detected_freq:.2f} Hz")
        print(f"   This matches the expected {expected_freq} Hz BPSK pattern!")
    else:
        print(f"\n⚠️  NO CLEAR PATTERN DETECTED")
        print(f"   Could not find frequency peak near {expected_freq} Hz")
        print(f"\n   Possible reasons:")
        print(f"   - Recording too dark (screen pattern not bright enough)")
        print(f"   - Subject too far from screen")
        print(f"   - Camera settings (exposure, auto-brightness)")
        print(f"   - Screen brightness too low")

    # Calculate brightness statistics
    brightness_std = np.std(brightness_values)
    brightness_range = np.max(brightness_values) - np.min(brightness_values)

    print(f"\nBrightness statistics:")
    print(f"  Mean: {np.mean(brightness_values):.2f}")
    print(f"  Std dev: {brightness_std:.2f}")
    print(f"  Range: {brightness_range:.2f}")

    if brightness_std < 5:
        print(f"  ⚠️  Low variation - pattern may not be visible enough")
    else:
        print(f"  ✓ Good variation - pattern has sufficient contrast")

    return {
        'pattern_detected': pattern_detected,
        'detected_freq': detected_freq,
        'brightness_values': brightness_values,
        'fps': fps,
        'frequencies': xf,
        'power_spectrum': power,
        'peaks': peaks,
        'brightness_std': brightness_std
    }


def plot_analysis(results, output_path=None):
    """Create plots showing the analysis results."""
    if results is None:
        return

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # Plot brightness over time
    ax1 = axes[0]
    time = np.arange(len(results['brightness_values'])) / results['fps']
    ax1.plot(time, results['brightness_values'], 'b-', linewidth=1)
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Average Brightness')
    ax1.set_title('Brightness Over Time')
    ax1.grid(True, alpha=0.3)

    # Plot frequency spectrum
    ax2 = axes[1]
    ax2.plot(results['frequencies'], results['power_spectrum'], 'r-', linewidth=1)

    # Mark peaks
    if len(results['peaks']) > 0:
        peak_freqs = results['frequencies'][results['peaks']]
        peak_powers = results['power_spectrum'][results['peaks']]
        ax2.plot(peak_freqs, peak_powers, 'go', markersize=8, label='Detected peaks')

    # Mark expected frequency
    ax2.axvline(x=3.0, color='orange', linestyle='--', linewidth=2, label='Expected (3 Hz)')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Power')
    ax2.set_title('Frequency Spectrum')
    ax2.set_xlim(0, 15)
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"\nPlot saved to: {output_path}")

    plt.show()


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("VeriLight Screen Embedding - Recording Test")
    print("="*60 + "\n")

    if len(sys.argv) < 2:
        print("Usage: python test_recording.py <video_path>")
        print("\nExample:")
        print("  python test_recording.py recordings/recording_20250101_120000.mp4")
        return

    video_path = sys.argv[1]

    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found: {video_path}")
        return

    # Analyze video
    results = analyze_video_for_pattern(video_path, sample_duration=5)

    if results is None:
        return

    # Create output directory for plots
    output_dir = os.path.dirname(video_path) or "."
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    plot_path = os.path.join(output_dir, f"{video_name}_analysis.png")

    # Generate plots
    print("\nGenerating analysis plots...")
    plot_analysis(results, output_path=plot_path)

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if results['pattern_detected']:
        print("✅ SUCCESS: BPSK pattern detected in video!")
        print(f"\nThe screen embedding is working. The {results['detected_freq']:.2f} Hz")
        print("blinking pattern is visible in the recorded facial video.")
        print("\nNext steps:")
        print("  - Try the full VeriLight verification pipeline:")
        print(f"    python verify.py {video_path} {output_dir}/verification_output")
    else:
        print("⚠️  WARNING: Could not clearly detect BPSK pattern")
        print("\nTroubleshooting tips:")
        print("  1. Record in a darker room")
        print("  2. Sit closer to the laptop screen (2-3 feet)")
        print("  3. Increase screen brightness to 100%")
        print("  4. Make sure your face is well-lit by the screen")
        print("  5. Try recording for longer (15-30 seconds)")
        print("  6. Check camera exposure settings (disable auto-exposure if possible)")

    print("="*60 + "\n")


if __name__ == "__main__":
    main()
