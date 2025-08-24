import os
import glob
import subprocess
import shutil
import mido
import pygame

class MidiVisualizer:
    """
    A class to generate MIDI visualizations by rendering frames
    with Pygame and compiling them into a video with FFmpeg.
    """
    def __init__(self, width=1280, height=720, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.temp_dir = 'temp_frames'
        self.piano_key_width = 10
        self.falling_note_speed = 5

    def render_video(self, midi_path, output_path):
        """
        Renders a MIDI file visualization to a video file.

        Args:
            midi_path (str): Path to the input MIDI file.
            output_path (str): Path for the output video file.
        """
        if not os.path.exists(midi_path):
            raise FileNotFoundError(f"MIDI file not found at {midi_path}")

        # Prepare directories for frames
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)

        print(f"DEBUG: Rendering frames to {self.temp_dir}...")

        # Initialize Pygame
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        
        # Load MIDI file
        try:
            mid = mido.MidiFile(midi_path)
        except Exception as e:
            raise RuntimeError(f"Error loading MIDI file: {e}")

        # Rendering loop
        frame_count = 0
        note_on_events = []
        
        for msg in mid.play():
            if msg.type == 'note_on' and msg.velocity > 0:
                note_on_events.append({'time': msg.time, 'note': msg.note})
            
            # Clear screen
            screen.fill((0, 0, 0))
            
            # Draw falling notes (simplified for this example)
            for event in note_on_events:
                # Draw a note based on its time and speed
                x = (event['note'] % 12) * self.piano_key_width + (event['note'] // 12) * 20
                y = self.height - (msg.time - event['time']) * self.falling_note_speed * self.fps
                pygame.draw.rect(screen, (75, 105, 177), (x, y, self.piano_key_width, 20))
                
            pygame.display.flip()
            
            # Save frame
            frame_filename = os.path.join(self.temp_dir, f'frame_{frame_count:06d}.png')
            pygame.image.save(screen, frame_filename)
            frame_count += 1
            
        pygame.quit()
        
        print(f"DEBUG: All frames rendered. Now compiling video with FFmpeg...")
        
        # FFmpeg command to compile images into a video
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',
            '-r', str(self.fps),
            '-i', os.path.join(self.temp_dir, 'frame_%06d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            output_path
        ]

        try:
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"SUCCESS: Video saved to: {output_path}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"An error occurred during FFmpeg execution: {e}")

        # Clean up temporary frames
        shutil.rmtree(self.temp_dir)
        print("DEBUG: Cleaned up temporary files.")

