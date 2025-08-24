import pygame
import mido
import os
import shutil
import moviepy
try:
    from moviepy.editor import ImageSequenceClip
except ImportError:
    try:
        from moviepy.video.tools.subclip import ImageSequenceClip
    except ImportError:
        raise ImportError(
            "The required 'moviepy' module or its components could not be found. "
            "Please ensure you have a compatible version of moviepy installed.")
from mido.midifiles.tracks import MidiTrack
import time

class MidiVisualizer:
    """
    Renders a MIDI file into a custom-style video using Pygame and MoviePy.
    """
    def __init__(self, midi_file, output_video, resolution=(1280, 720), fps=60, note_speed=0.5):
        self.midi_file = midi_file
        self.output_video = output_video
        self.resolution = resolution
        self.fps = fps
        self.note_speed = note_speed
        self.width, self.height = self.resolution
        
        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode(self.resolution)
        self.clock = pygame.time.Clock()
        
        # Colors
        self.BACKGROUND_COLOR = (0, 0, 0)
        self.NOTE_COLOR = (255, 255, 255)
        self.KEY_COLOR = (200, 200, 200)
        self.KEY_ACTIVE_COLOR = (255, 255, 0)

        # Temporary directory for frames
        self.temp_dir = 'temp_frames'
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)

        # MIDI parsing
        self.notes = self._parse_midi()
        self.total_time_seconds = self._get_midi_duration()

    def _parse_midi(self):
        """
        Parses the MIDI file to extract note on/off events with their timestamps.
        """
        notes = []
        midi = mido.MidiFile(self.midi_file)
        time = 0
        for track in midi.tracks:
            for msg in track:
                time += msg.time
                if msg.type in ['note_on', 'note_off'] and msg.velocity > 0:
                    notes.append({
                        'key': msg.note,
                        'time': mido.tick2second(time, midi.ticks_per_beat, 500000),  # Convert ticks to seconds
                        'type': msg.type
                    })
        return notes

    def _get_midi_duration(self):
        """
        Calculates the total duration of the MIDI file in seconds.
        """
        end_time = 0
        current_time = 0
        for msg in mido.MidiFile(self.midi_file).tracks[0]:
            current_time += mido.tick2second(msg.time, mido.MidiFile(self.midi_file).ticks_per_beat, 500000)
            if msg.is_meta and msg.type == 'end_of_track':
                end_time = current_time
                break
        return end_time

    def _draw_piano_keys(self, active_keys):
        """
        Draws the piano keyboard at the bottom of the screen.
        """
        # This is a simplified drawing. For a more realistic look, you'd handle black keys separately.
        num_keys = 88  # A standard piano
        key_width = self.width / num_keys
        
        for i in range(num_keys):
            key_rect = pygame.Rect(i * key_width, self.height - 50, key_width, 50)
            color = self.KEY_ACTIVE_COLOR if i + 21 in active_keys else self.KEY_COLOR
            pygame.draw.rect(self.screen, color, key_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), key_rect, 1)

    def _draw_falling_notes(self, current_time, active_notes):
        """
        Draws the falling notes based on their position.
        """
        fall_distance = self.height * self.note_speed  # How far a note travels
        
        for note in self.notes:
            if note['type'] == 'note_on' and note['time'] <= current_time:
                note_start_time = note['time']
                
                # Find the corresponding note_off event
                note_end_time = next((n['time'] for n in self.notes if n['type'] == 'note_off' and n['key'] == note['key'] and n['time'] > note_start_time), current_time)
                
                duration = note_end_time - note_start_time
                
                # Calculate the top and bottom y-coordinates of the note
                y_top = self.height - (self.height - (note_start_time - current_time) * fall_distance)
                y_bottom = self.height - (self.height - (note_end_time - current_time) * fall_distance)
                
                # Draw the note if it's within the screen bounds
                if y_bottom >= 0 and y_top <= self.height:
                    key_pos = note['key'] - 21 # Offset for standard MIDI piano range
                    num_keys = 88
                    key_width = self.width / num_keys
                    x = key_pos * key_width
                    width = key_width
                    
                    note_rect = pygame.Rect(x, y_top, width, y_bottom - y_top)
                    pygame.draw.rect(self.screen, self.NOTE_COLOR, note_rect)
    
    def render_video(self):
        """
        Main rendering loop. Generates frames and compiles them into a video.
        """
        frame_number = 0
        total_frames = int(self.total_time_seconds * self.fps)
        
        for frame_number in range(total_frames):
            current_time = frame_number / self.fps
            
            # Get active keys for the current frame
            active_keys = set()
            for note in self.notes:
                if note['type'] == 'note_on' and note['time'] <= current_time:
                    end_time = next((n['time'] for n in self.notes if n['type'] == 'note_off' and n['key'] == note['key'] and n['time'] > note['time']), current_time)
                    if end_time >= current_time:
                        active_keys.add(note['key'])

            # Clear screen
            self.screen.fill(self.BACKGROUND_COLOR)
            
            # Draw elements
            self._draw_piano_keys(active_keys)
            self._draw_falling_notes(current_time, active_keys)
            
            # Save frame
            frame_path = os.path.join(self.temp_dir, f"frame_{frame_number:05d}.png")
            pygame.image.save(self.screen, frame_path)
        
        print(f"Rendering complete. Compiling video...")
        
        # Compile video from frames
        try:
            clip = ImageSequenceClip(self.temp_dir, fps=self.fps)
            clip.write_videofile(self.output_video, fps=self.fps, codec="libx264")
        finally:
            # Clean up temporary frames
            shutil.rmtree(self.temp_dir)
            
        print(f"Video saved to {self.output_video}")

if __name__ == '__main__':
    # Example usage. Make sure you have a 'your_song.mid' file in the same directory.
    visualizer = MidiVisualizer(
        midi_file="your_song.mid",
        output_video="my_amazing_video.mp4",
        resolution=(1920, 1080),
        fps=60,
        note_speed=0.5
    )
    visualizer.render_video()
