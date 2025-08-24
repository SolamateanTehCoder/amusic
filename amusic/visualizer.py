import os
import subprocess
import shutil
import mido
import pygame
import random

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
        self.note_speed = 600  # Pixels per second

        # Visual properties
        self.piano_key_height = 80
        self.piano_start_y = self.height - self.piano_key_height - 20
        # There are 52 white keys on an 88-key piano
        self.white_key_width = self.width / 52.0
        self.black_key_width = self.white_key_width * 0.6
        self.black_key_height = self.piano_key_height * 0.6

        # Colors
        self.white_key_color = (255, 255, 255)
        self.black_key_color = (0, 0, 0)
        self.note_color = (75, 105, 177)
        self.highlight_color = (75, 105, 177)
        self.background_color = (0, 0, 0)
        
        # Data structures for effects
        self.active_keys = {}
        self.particles = []

    def _get_key_x_position(self, note_number):
        """Calculates the x-position for a given MIDI note number on the piano."""
        midi_start_note = 21
        note_name_in_octave = note_number % 12
        black_key_indices = {1, 3, 6, 8, 10}

        # Calculate the position based on white keys
        white_key_count = 0
        for i in range(note_number - midi_start_note):
            if (midi_start_note + i) % 12 not in black_key_indices:
                white_key_count += 1
        
        x_pos = white_key_count * self.white_key_width
        
        # Adjust position for black keys
        if note_name_in_octave in black_key_indices:
            if note_name_in_octave in {1, 3}:
                # C# and D# are offset relative to the white key to their left
                x_pos = x_pos - self.white_key_width * 0.25
            elif note_name_in_octave in {6, 8, 10}:
                # F#, G#, A# are offset relative to the white key to their right
                x_pos = x_pos + self.white_key_width * 0.25
            x_pos -= self.black_key_width / 2
        
        return x_pos

    def _draw_piano(self, screen):
        """Draws a piano keyboard at the bottom of the screen."""
        black_key_indices = {1, 3, 6, 8, 10}
        
        # First, draw all white keys
        white_key_count = 0
        for i in range(88):
            midi_note = 21 + i
            note_name_in_octave = midi_note % 12
            
            if note_name_in_octave not in black_key_indices:
                x = white_key_count * self.white_key_width
                pygame.draw.rect(
                    screen,
                    self.white_key_color,
                    (x, self.piano_start_y, self.white_key_width, self.piano_key_height)
                )
                pygame.draw.rect(
                    screen,
                    (100, 100, 100),
                    (x, self.piano_start_y, self.white_key_width, self.piano_key_height),
                    1
                )
                white_key_count += 1
        
        # Then, draw all black keys on top
        white_key_count = 0
        for i in range(88):
            midi_note = 21 + i
            note_name_in_octave = midi_note % 12

            if note_name_in_octave in black_key_indices:
                if note_name_in_octave == 1: # C#
                    x = (white_key_count) * self.white_key_width - (self.black_key_width / 2)
                elif note_name_in_octave == 3: # D#
                    x = (white_key_count + 1) * self.white_key_width - (self.black_key_width / 2)
                elif note_name_in_octave == 6: # F#
                    x = (white_key_count + 2) * self.white_key_width - (self.black_key_width / 2)
                elif note_name_in_octave == 8: # G#
                    x = (white_key_count + 3) * self.white_key_width - (self.black_key_width / 2)
                elif note_name_in_octave == 10: # A#
                    x = (white_key_count + 4) * self.white_key_width - (self.black_key_width / 2)
                
                pygame.draw.rect(
                    screen,
                    self.black_key_color,
                    (x, self.piano_start_y, self.black_key_width, self.black_key_height)
                )
            
            if note_name_in_octave not in black_key_indices:
                white_key_count += 1

    def render_video(self, midi_path, output_path):
        """
        Renders a MIDI file visualization to a video file.
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

        # Pre-process all note on/off events into a timeline
        notes = []
        open_notes = {}
        total_time = 0.0

        for msg in mid.iter_track():
            total_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                open_notes[(msg.channel, msg.note)] = total_time
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if (msg.channel, msg.note) in open_notes:
                    start_time = open_notes.pop((msg.channel, msg.note))
                    notes.append({
                        'note': msg.note,
                        'start': start_time,
                        'end': total_time,
                        'duration': total_time - start_time
                    })
        
        # Add any notes that never received an 'off' message
        for (channel, note), start_time in open_notes.items():
            notes.append({
                'note': note,
                'start': start_time,
                'end': total_time,
                'duration': total_time - start_time
            })

        # Rendering loop
        total_frames = int(total_time * self.fps)
        
        for frame_count in range(total_frames):
            current_time = frame_count / self.fps
            
            screen.fill(self.background_color)
            self._draw_piano(screen)
            
            # Update and draw key highlights and particles
            self._update_effects(current_time)
            self._draw_effects(screen)
            
            # Draw falling notes
            for note in notes:
                # Check if the note is active in the current frame
                if current_time >= note['start'] and current_time < note['end']:
                    # Calculate the note's position
                    time_to_go = note['end'] - current_time
                    y_pos = self.piano_start_y - (self.note_speed * time_to_go)
                    
                    note_height = self.note_speed * note['duration']
                    
                    x_pos = self._get_key_x_position(note['note'])
                    
                    if x_pos is not None:
                        key_width = self.white_key_width
                        note_name = note['note'] % 12
                        if note_name in {1, 3, 6, 8, 10}:
                            key_width = self.black_key_width
                        
                        # Trigger effects when a note reaches the key
                        if y_pos <= self.piano_start_y and note['note'] not in self.active_keys:
                            self.active_keys[note['note']] = {'start_time': current_time, 'duration': 0.1}
                            self._create_particles(x_pos + key_width / 2, self.piano_start_y)

                        pygame.draw.rect(screen, self.note_color, (x_pos, y_pos, key_width, note_height))
            
            pygame.display.flip()
            
            frame_filename = os.path.join(self.temp_dir, f'frame_{frame_count:06d}.png')
            pygame.image.save(screen, frame_filename)
            
        pygame.quit()
        
        print(f"DEBUG: All frames rendered. Now compiling video with FFmpeg...")
        
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

    def _update_effects(self, current_time):
        """Updates the state of active key highlights and particles."""
        # Update active keys
        keys_to_remove = [note for note, data in self.active_keys.items() if current_time - data['start_time'] > data['duration']]
        for note in keys_to_remove:
            del self.active_keys[note]

        # Update particles
        self.particles = [p for p in self.particles if p['alpha'] > 0]
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['alpha'] -= 10
            p['size'] -= 0.1

    def _draw_effects(self, screen):
        """Draws key highlights and particles."""
        # Draw key highlights
        for note in self.active_keys:
            x_pos = self._get_key_x_position(note)
            key_width = self.white_key_width
            note_name = note % 12
            if note_name in {1, 3, 6, 8, 10}:
                key_width = self.black_key_width
            
            highlight_surface = pygame.Surface((key_width, self.piano_key_height), pygame.SRCALPHA)
            highlight_surface.fill(self.highlight_color + (80,)) # Semi-transparent
            screen.blit(highlight_surface, (x_pos, self.piano_start_y))

        # Draw particles
        for p in self.particles:
            if p['alpha'] > 0:
                particle_color = p['color'] + (int(p['alpha']),)
                pygame.draw.circle(screen, particle_color, (int(p['x']), int(p['y'])), int(p['size']))

    def _create_particles(self, x, y, count=10):
        """Creates a burst of particles at a given position."""
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(1, 3)
            vx = speed * pygame.math.Vector2(1, 0).rotate(angle)[0]
            vy = speed * pygame.math.Vector2(1, 0).rotate(angle)[1]

            self.particles.append({
                'x': x,
                'y': y,
                'vx': vx,
                'vy': vy,
                'alpha': 255,
                'size': random.uniform(2, 5),
                'color': self.note_color
            })
