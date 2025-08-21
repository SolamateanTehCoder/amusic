# Amusic

A Python package designed to generate engaging MIDI visualization videos with animated falling notes, leveraging the `synthviz` library. This tool includes a pre-processing step to ensure clear visual separation of rapid, consecutive notes on the same key.

---

## Features

* **MIDI to Video:** Converts MIDI files into dynamic video visualizations.

* **Visual Note Separation:** Automatically adjusts note durations to create clear visual gaps for fast, repeated notes on the same key.

* **Customizable Output:** Control video resolution, frame rate, note falling speed, and more.

* **Cross-Platform:** Designed to work on Windows, macOS, and Linux.

---

## System Requirements

Before installing the Python package, ensure you have the following system-level dependencies installed on your operating system:

* **FFmpeg:** A powerful tool for handling multimedia files (video and audio).

    * **Ubuntu/Debian:** `sudo apt-get update && sudo apt-get install -y ffmpeg`

    * **macOS (with Homebrew):** `brew install ffmpeg`

    * **Windows:** Download from the [FFmpeg website](https://ffmpeg.org/download.html) and add to your system's PATH.

* **Timidity:** A MIDI sequencer that `synthviz` uses for audio synthesis.

    * **Ubuntu/Debian:** `sudo apt-get update && sudo apt-get install -y timidity`

    * **macOS (with Homebrew):** `brew install timidity`

    * **Windows:** Download a Windows binary (e.g., from [here](https://www.google.com/search?q=https://sourceforge.net/projects/timidity/files/timidity%2B%2B/)) and add to your system's PATH.

---

## Installation
* **pip install amusic** *
## Usage

Once installed, you can use the `MidiVisualizer` class in your Python scripts:

```python
from amusic.visualizer import MidiVisualizer
import os

# --- Configuration ---
# Replace 'your_midi_file.midi' with the path to your MIDI file
MIDI_FILE = "your_midi_file.midi"
OUTPUT_VIDEO = "my_midi_video.mp4"

# --- Create and run the visualizer ---
if os.path.exists(MIDI_FILE):
    visualizer = MidiVisualizer(
        midi_file_path=MIDI_FILE,
        output_video_filename=OUTPUT_VIDEO,
        resolution=(1920, 1080),  # Example: Full HD resolution
        fps=60,                   # Example: Higher frame rate
        min_visual_gap_seconds=0.04 # Example: Adjust gap for visual clarity
    )
    visualizer.create_visualizer_video()
    print(f"Video saved to: {OUTPUT_VIDEO}")
else:
    print(f"Error: MIDI file '{MIDI_FILE}' not found. Please provide a valid path.")
