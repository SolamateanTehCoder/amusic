import sys
import os
import glob
import subprocess
import shutil
import mido
import pygame

# --- Configuration ---
MIDI_FILE = 'direct_output.midi'
OUTPUT_VIDEO = 'rendered_video.mp4'

# Video properties
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
VIDEO_FPS = 30

# Visual properties
PIANO_KEY_WIDTH = 10
FALLING_NOTE_SPEED = 5

def main():
    """
    Main function to run the video rendering process.
    """
    if not os.path.exists(MIDI_FILE):
        print(f"Error: MIDI file not found at {MIDI_FILE}")
        sys.exit(1)

    # Prepare directories
    temp_dir = 'temp_frames'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    print(f"DEBUG: Rendering frames to {temp_dir}...")

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((VIDEO_WIDTH, VIDEO_HEIGHT))
    
    # Load MIDI file
    try:
        mid = mido.MidiFile(MIDI_FILE)
    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        sys.exit(1)

    # Rendering loop
    frame_count = 0
    note_on_events = []
    
    for msg in mid.play():
        if msg.type == 'note_on' and msg.velocity > 0:
            note_on_events.append({'time': msg.time, 'note': msg.note})
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw falling notes and pressed keys (simplified for this example)
        for event in note_on_events:
            # Draw a note based on its time and speed
            x = (event['note'] % 12) * PIANO_KEY_WIDTH + (event['note'] // 12) * 20
            y = VIDEO_HEIGHT - (msg.time - event['time']) * FALLING_NOTE_SPEED * VIDEO_FPS
            pygame.draw.rect(screen, (75, 105, 177), (x, y, PIANO_KEY_WIDTH, 20))
            
        pygame.display.flip()
        
        # Save frame
        frame_filename = os.path.join(temp_dir, f'frame_{frame_count:06d}.png')
        pygame.image.save(screen, frame_filename)
        frame_count += 1
        
    pygame.quit()
    
    print(f"DEBUG: All frames rendered. Now compiling video with FFmpeg...")
    
    # FFmpeg command to compile images into a video
    # -framerate: specifies the frame rate of the input images
    # -i: input file pattern
    # -c:v: video codec (libx264 is a good default)
    # -pix_fmt: pixel format
    # -y: overwrite output file if it exists
    # final output file
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',
        '-r', str(VIDEO_FPS),
        '-i', os.path.join(temp_dir, 'frame_%06d.png'),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        OUTPUT_VIDEO
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"SUCCESS: Video saved to: {OUTPUT_VIDEO}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during FFmpeg execution: {e}")
        sys.exit(1)

    # Clean up temporary frames
    shutil.rmtree(temp_dir)
    print("DEBUG: Cleaned up temporary files.")


if __name__ == "__main__":
    main()

