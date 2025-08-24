# amusic

A custom MIDI visualization tool designed to render videos.

This project moves away from pre-built visualization libraries like `synthviz` to provide a flexible, frame-by-frame rendering pipeline built with `pygame` and `moviepy`.

## ✨ Features

* **Custom Rendering Engine**: Render notes as falling sprites rather than simple bars.

* **Real-time Key Lighting**: Piano keys at the bottom light up as notes are played.

* **Full Control**: Customize resolution, frame rate, and other visual elements.

* **MIDI Support**: Processes standard MIDI files (`.mid`).

## ⚙️ Requirements

To run this project, you need:

* **Python 3.6+**

* **FFmpeg**: Required by `moviepy` to render the video. You can install it on your system with a package manager (e.g., `brew install ffmpeg` on macOS, `sudo apt-get install ffmpeg` on Ubuntu).

The Python dependencies are handled by `pip` automatically.

## 📥 Installation

You can install `amusic` directly from the Python Package Index (PyPI).

```
pip install amusic
```

If you plan to modify the code, you can also clone the repository and install it in editable mode. This links your environment to your local files, so any changes you make are instantly available.

```
# Clone the repository
git clone [https://github.com/SolamateanTehCoder/amusic.git](https://github.com/SolamateanTehCoder/amusic.git)
cd amusic

# Install in editable mode
pip install -e .
```

## 🚀 Usage

Here is a simple example of how to use the `MidiVisualizer` class to generate a video.

```
from amusic import MidiVisualizer

# Create a visualizer instance
visualizer = MidiVisualizer(
    midi_file="your_song.mid",
    output_video="my_amazing_video.mp4",
    resolution=(1920, 1080),
    fps=60,
    note_speed=0.5  # Adjust this value to change how fast notes fall
)

# Render the video
visualizer.render_video()
```

## 🤝 Contributing

Contributions are welcome! If you have suggestions for new features, bug fixes, or improvements, feel free to open an issue or submit a pull request.
