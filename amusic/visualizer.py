import mido
import os
import shutil
import sys
import subprocess

try:
    from synthviz import create_video as synthviz_create_video
    print("DEBUG: synthviz imported successfully.")
except ImportError:
    print("ERROR: synthviz not found. Please install it using: pip install synthviz")
    print("Exiting as synthviz is required for this version of the visualizer.")
    sys.exit(1)

class MidiVisualizer:
    """
    A Python module for generating MIDI visualization videos using synthviz,
    with built-in MIDI pre-processing for visual note separation.

    Designed to be cross-platform (Windows, macOS, Linux).
    Requires system dependencies: FFmpeg and Timidity.
    """

    def __init__(self, midi_file_path, output_video_filename=None,
                 resolution=(1920, 1080), fps=60, bitrate_mbps=10, # Updated default resolution and FPS
                 max_video_duration_seconds=30, black_key_height_ratio=0.6,
                 synthviz_vertical_speed=0.25, min_visual_gap_seconds=0.04): # Updated defaults
        """
        Initializes the MidiVisualizer with configuration settings.

        Args:
            midi_file_path (str): The path to the input MIDI file.
            output_video_filename (str, optional): The name of the output video file.
                                                  Defaults to MIDI_FILE_NAME_visualizer_final.mp4.
            resolution (tuple, optional): Video resolution (width, height). Defaults to (1920, 1080).
            fps (int, optional): Frames per second. Defaults to 60.
            bitrate_mbps (int, optional): Video bitrate in megabits per second. Defaults to 10.
            max_video_duration_seconds (int, optional): Maximum duration of the output video in seconds.
                                                        Used to limit processing time. Defaults to 30.
            black_key_height_ratio (float, optional): Height of black keys as a ratio of full piano height (0.0 to 1.0).
                                                      Defaults to 0.6.
            synthviz_vertical_speed (float, optional): The speed of falling keys in synthviz,
                                                       fraction of image height per second. Defaults to 0.25.
            min_visual_gap_seconds (float, optional): Minimum visual gap to force between consecutive notes
                                                      on the same key in seconds. Defaults to 0.04.
        """
        self.midi_file_path = midi_file_path
        self.output_video_filename = output_video_filename if output_video_filename else \
                                     os.path.splitext(os.path.basename(midi_file_path))[0] + "_visualizer_final.mp4"
        self.resolution = resolution
        self.fps = fps
        self.bitrate_mbps = bitrate_mbps
        self.max_video_duration_seconds = max_video_duration_seconds
        self.black_key_height_ratio = black_key_height_ratio
        self.synthviz_vertical_speed = synthviz_vertical_speed
        self.min_visual_gap_seconds = min_visual_gap_seconds

        self._validate_config()
        print(f"DEBUG: Configuration loaded: Resolution={self.resolution}, FPS={self.fps}, Bitrate={self.bitrate_mbps}Mbps, Max Video Duration={self.max_video_duration_seconds}s, Black Key Height Ratio={self.black_key_height_ratio}, Synthviz Vertical Speed={self.synthviz_vertical_speed}, Min Visual Gap Seconds={self.min_visual_gap_seconds}")

    def _validate_config(self):
        """Internal method to validate configuration parameters."""
        if not isinstance(self.resolution, tuple) or len(self.resolution) != 2 or not all(isinstance(i, int) and i > 0 for i in self.resolution):
            raise ValueError("RESOLUTION must be a tuple of two positive integers (e.g., (1280, 720)).")
        if not isinstance(self.fps, int) or self.fps <= 0:
            raise ValueError("FPS must be a positive integer.")
        if not isinstance(self.bitrate_mbps, (int, float)) or self.bitrate_mbps <= 0:
            raise ValueError("BITRATE_MBPS must be a positive number.")
        if not isinstance(self.max_video_duration_seconds, (int, float)) or self.max_video_duration_seconds <= 0:
            raise ValueError("MAX_VIDEO_DURATION_SECONDS must be a positive number.")
        if not isinstance(self.black_key_height_ratio, (int, float)) or not (0 <= self.black_key_height_ratio <= 1.0):
            raise ValueError("BLACK_KEY_HEIGHT_RATIO must be a number between 0.0 and 1.0.")
        if not isinstance(self.synthviz_vertical_speed, (int, float)) or self.synthviz_vertical_speed <= 0:
            raise ValueError("SYNTHVIZ_VERTICAL_SPEED must be a positive number.")
        if not isinstance(self.min_visual_gap_seconds, (int, float)) or self.min_visual_gap_seconds < 0:
            raise ValueError("MIN_VISUAL_GAP_SECONDS must be a non-negative number.")

    def _check_system_dependencies(self):
        """
        Checks for the presence of required system dependencies (ffmpeg, timidity).
        Raises an error if a dependency is not found.
        """
        dependencies = ['ffmpeg', 'timidity']
        for dep in dependencies:
            if shutil.which(dep) is None:
                raise RuntimeError(f"Required system dependency '{dep}' not found in PATH. "
                                   f"Please install it. (e.g., on Ubuntu: sudo apt-get install -y {dep})")
        print("DEBUG: All system dependencies (ffmpeg, timidity) found.")


    def _parse_midi_and_apply_visual_gaps(self):
        """
        Parses the input MIDI file, extracts note events, applies visual gap adjustments,
        and reconstructs a new temporary MIDI file.

        Returns:
            tuple: (path_to_temp_midi_file: str, total_midi_duration_seconds: float)
                   Returns (None, 0) if an error occurs.
        """
        print(f"DEBUG: Parsing MIDI and applying visual gaps from '{self.midi_file_path}'")
        try:
            in_midi = mido.MidiFile(self.midi_file_path)
            
            notes_with_abs_times = []
            active_notes_tracking = {} # {note_number: {'start_time': ..., 'original_velocity': ...}}
            
            all_original_messages_with_abs_time = []
            current_global_time_seconds = 0.0
            current_tempo_us_per_beat = mido.bpm2tempo(120) # Default to 120 BPM (microseconds per beat)

            # First pass: Collect all events with absolute times and track tempo changes
            for msg in mido.merge_tracks(in_midi.tracks):
                # Calculate time in seconds for the current message's delta
                # mido.tick2second needs: time_in_ticks, ticks_per_beat, tempo_in_us_per_beat
                delta_seconds = mido.tick2second(msg.time, in_midi.ticks_per_beat, current_tempo_us_per_beat)
                current_global_time_seconds += delta_seconds
                
                if msg.type == 'set_tempo':
                    current_tempo_us_per_beat = msg.tempo
                
                all_original_messages_with_abs_time.append({'time': current_global_time_seconds, 'msg': msg.copy()})

                if msg.type == 'note_on' and msg.velocity > 0:
                    active_notes_tracking[msg.note] = {
                        'start_time': current_global_time_seconds,
                        'original_velocity': msg.velocity,
                    }
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    if msg.note in active_notes_tracking:
                        start_info = active_notes_tracking.pop(msg.note)
                        notes_with_abs_times.append({
                            'note': msg.note,
                            'start': start_info['start_time'],
                            'end': current_global_time_seconds,
                            'velocity': start_info['original_velocity']
                        })
            
            # Handle notes that might not have received a note_off by end of MIDI
            final_total_time = current_global_time_seconds
            for note_num, start_info in active_notes_tracking.items():
                notes_with_abs_times.append({
                    'note': note_num,
                    'start': start_info['start_time'],
                    'end': final_total_time,
                    'velocity': start_info['original_velocity']
                })

            notes_with_abs_times.sort(key=lambda x: x['start'])

            # Step 2: Apply visual gap adjustment to notes
            modified_notes = []
            for i, note_info in enumerate(notes_with_abs_times):
                new_end_time = note_info['end']

                # Check if there's a next note on the same key very soon
                if i + 1 < len(notes_with_abs_times):
                    next_note_info = notes_with_abs_times[i+1]
                    if next_note_info['note'] == note_info['note']:
                        gap_between_notes = next_note_info['start'] - note_info['end']
                        
                        # If the gap is smaller than our desired visual gap, shorten the current note
                        if 0 <= gap_between_notes < self.min_visual_gap_seconds:
                            proposed_new_end = note_info['end'] - self.min_visual_gap_seconds
                            new_end_time = max(note_info['start'], proposed_new_end)
                        elif gap_between_notes < 0: # Overlapping notes
                            new_end_time = min(note_info['end'], next_note_info['start'] - 0.001) # Small buffer
                            new_end_time = max(note_info['start'], new_end_time) # Ensure not before start

                # Add the modified note to our list
                modified_notes.append({
                    'note': note_info['note'],
                    'start': note_info['start'],
                    'end': new_end_time,
                    'velocity': note_info['velocity']
                })

            # Step 3: Reconstruct a new MIDI file
            temp_midi_file = "temp_processed_midi.mid"
            out_midi = mido.MidiFile(ticks_per_beat=in_midi.ticks_per_beat, type=in_midi.type)
            out_track = mido.MidiTrack() # We'll put all main events in track 0 for simplicity and compatibility
            out_midi.tracks.append(out_track)

            # Collect all events for rebuilding the single main track
            rebuild_events = []
            
            # Add processed note_on/off events
            for note in modified_notes:
                if note['start'] < note['end']:
                    rebuild_events.append({'time': note['start'], 'type': 'note_event', 'note': note['note'], 'velocity': note['velocity'], 'msg_type_name': 'note_on'})
                    rebuild_events.append({'time': note['end'], 'type': 'note_event', 'note': note['note'], 'velocity': 0, 'msg_type_name': 'note_off'})
            
            # Add original meta messages (especially set_tempo) and other non-note messages
            # Filter for non-note messages from the original merged stream
            for event_info in all_original_messages_with_abs_time:
                if event_info['msg'].type != 'note_on' and event_info['msg'].type != 'note_off':
                    rebuild_events.append({'time': event_info['time'], 'type': 'original_msg_wrapper', 'msg': event_info['msg'].copy()})
            
            # Sort all events chronologically
            rebuild_events.sort(key=lambda x: x['time'])

            # Reconstruct the single main track with correct delta times and tempo handling
            current_track_time_seconds = 0.0
            current_track_tempo_us_per_beat = mido.bpm2tempo(120) # Start with default tempo

            for event in rebuild_events:
                delta_time_seconds = event['time'] - current_track_time_seconds
                
                # Calculate delta ticks
                beats_per_second = 1_000_000.0 / current_track_tempo_us_per_beat
                ticks_per_second = beats_per_second * out_midi.ticks_per_beat
                delta_time_ticks = max(0, int(round(delta_time_seconds * ticks_per_second)))

                msg_to_append = None # Initialize message to append

                if event['type'] == 'note_event': # This is our custom note event type
                    if event['msg_type_name'] == 'note_on':
                        msg_to_append = mido.Message('note_on', note=event['note'], velocity=event['velocity'], time=delta_time_ticks)
                    elif event['msg_type_name'] == 'note_off':
                        # For note_off, it's typically velocity 0 as per MIDI spec for ending a note
                        msg_to_append = mido.Message('note_off', note=event['note'], velocity=0, time=delta_time_ticks)
                elif event['type'] == 'original_msg_wrapper': # This wraps an original mido message
                    msg_to_append = event['msg']
                    msg_to_append.time = delta_time_ticks # Update delta time for the message
                    if msg_to_append.type == 'set_tempo':
                        current_track_tempo_us_per_beat = msg_to_append.tempo # Update current tempo

                if msg_to_append: # Only append if a message was successfully created
                    out_track.append(msg_to_append)
                    current_track_time_seconds = event['time'] # Update track's absolute time
            
            # Ensure end_of_track message
            # Check if any message in out_track is an end_of_track message, by checking its type
            if not any(msg.type == 'end_of_track' for msg in out_track):
                out_track.append(mido.Message('end_of_track', time=0))

            out_midi.save(temp_midi_file)
            print(f"DEBUG: Modified MIDI saved to '{temp_midi_file}'")
            return temp_midi_file, final_total_time # Return path to new MIDI and original total time

        except Exception as e:
            print(f"ERROR: An error occurred during MIDI pre-processing for gaps: {e}")
            return None, 0

    def create_visualizer_video(self):
        """
        Main function to create the MIDI visualizer video.
        This method orchestrates the MIDI pre-processing and video generation.
        """
        print("\n--- Starting MIDI Visualizer Creation Process ---")
        
        # Step 0: Check system dependencies
        try:
            self._check_system_dependencies()
        except RuntimeError as e:
            print(f"CRITICAL ERROR: {e}")
            sys.exit(1)

        # Step 1: Pre-process MIDI for visual gaps
        processed_midi_file, total_midi_time = self._parse_midi_and_apply_visual_gaps()
        
        if processed_midi_file is None or total_midi_time == 0:
            print("ERROR: MIDI pre-processing failed or no notes found. Cannot proceed with video creation.")
            sys.exit(1)
        clipped_duration = min(total_midi_time, self.max_video_duration_seconds)
        
        # --- Use synthviz to create the video WITH audio ---
        print("\n--- Generating video and audio using synthviz ---")
        try:
            synthviz_create_video(
                input_midi=processed_midi_file, # Use the processed MIDI file
                video_filename=self.output_video_filename,
                image_width=self.resolution[0],
                image_height=self.resolution[1],
                black_key_height=self.black_key_height_ratio,
                vertical_speed=self.synthviz_vertical_speed,
                fps=self.fps
            )
            print(f"\nSUCCESS: Final video successfully created as '{self.output_video_filename}' using synthviz.")
        except Exception as e:
            print(f"ERROR: Failed to generate video using synthviz: {e}")
            print("HINT: Ensure synthviz is installed and your MIDI file is valid. Check synthviz's documentation for any specific dependencies for audio rendering (e.g., soundfonts or specific backend programs like Timidity).")
            sys.exit(1)
        finally:
            # Clean up the temporary processed MIDI file
            if os.path.exists(processed_midi_file):
                try:
                    os.remove(processed_midi_file)
                    print(f"DEBUG: Removed temporary processed MIDI file: '{processed_midi_file}'")
                except Exception as e:
                    print(f"WARNING: Failed to remove temporary processed MIDI file '{processed_midi_file}': {e}")
            print("--- Video creation process complete ---")
