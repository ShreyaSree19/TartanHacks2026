import numpy as np
import librosa
import soundfile as sf
import json
import os
import pretty_midi
from basic_pitch.inference import predict
from scipy.signal import butter, sosfilt
from pathlib import Path

# --- PREPROCESSING UTILITY ---

def preprocess_audio(y, sr, lowcut=80.0, highcut=880.0):
    """
    Applies a Butterworth bandpass filter to clean up vocals for MIDI extraction.
    Restricts frequencies to the typical human melodic range.
    """
    print(f"  > Preprocessing: Bandpass Filter ({lowcut}Hz - {highcut}Hz)")
    
    nyquist = 0.5 * sr
    low = lowcut / nyquist
    high = highcut / nyquist
    
    # 5th order Butterworth filter for a sharp cutoff without phase distortion
    sos = butter(5, [low, high], btype='band', output='sos')
    filtered_y = sosfilt(sos, y)
    
    # Normalize to ensure Basic Pitch has a strong signal to analyze
    filtered_y = librosa.util.normalize(filtered_y)
    
    return filtered_y

def extract_melody(vocal_path, output_filename='mil_dreams_low_priority.mid', bpm=120):
    
    y, sr = librosa.load(vocal_path, sr=None)
    y_filtered = preprocess_audio(y, sr)
    
    temp_filtered_path = "temp_vocal_cleaned.wav"
    sf.write(temp_filtered_path, y_filtered, sr)

    _, midi_data, _ = predict(temp_filtered_path)

    for instrument in midi_data.instruments:
        # 1. NEW SORTING: Sort by start time, then by PITCH (lowest first)
        # This ensures the 'accepted' note is the bottom one in an octave pair
        instrument.notes.sort(key=lambda x: (x.start, x.pitch))
        
        cleaned_notes = []
        if instrument.notes:
            for current_note in instrument.notes:
                if not cleaned_notes:
                    cleaned_notes.append(current_note)
                    continue
                
                # Reference the last note we successfully added
                last_note = cleaned_notes[-1]
                
                # --- OCTAVE JUMP PREVENTION LOGIC ---
                # Check if it's the same pitch class (e.g., C) but a different octave
                # (Note: abs(diff) % 12 == 0 ensures it's exactly 12, 24, etc. semitones apart)
                pitch_diff = current_note.pitch - last_note.pitch
                
                if pitch_diff > 0 and pitch_diff % 12 == 0:
                    # Force the current note to match the previous octave
                    current_note.pitch = last_note.pitch
                
                # --- GHOST/OVERLAP PREVENTION ---
                # If notes start at nearly the same time and are the same pitch (now corrected)
                is_ghost = False

                is_ghost = False
                
                for accepted in cleaned_notes:
                    # If notes start at the same time
                    if abs(current_note.start - accepted.start) < 0.05:
                        interval = abs(current_note.pitch - accepted.pitch)
                        # If it's the same note or an octave higher, skip it
                        if interval == 0 or interval % 12 == 0:
                            is_ghost = True
                            break
                
                if not is_ghost:
                    cleaned_notes.append(current_note)

        # 2. Monophonic Truncation (No two notes at once)
        final_notes = []
        if cleaned_notes:
            cleaned_notes.sort(key=lambda x: x.start)
            active = cleaned_notes[0]
            for next_n in cleaned_notes[1:]:
                if next_n.start < active.end:
                    active.end = next_n.start 
                
                if active.end > active.start + 0.05:
                    final_notes.append(active)
                active = next_n
            final_notes.append(active)

        instrument.notes = final_notes
        
        # Reset velocity for a clean score
        for n in instrument.notes:
            n.velocity = 100

    midi_data.write(output_filename)
    if os.path.exists(temp_filtered_path): os.remove(temp_filtered_path)
    print(f"Success: Saved lower-octave priority MIDI to {output_filename}")
    return output_filename


def extract_chords(instrumental_path, output_filename='chords.json'):
    """Analyzes harmonic content to identify major/minor chords."""
    print(f"\n--- Stage 2B: Processing Chords from {instrumental_path} ---")
    
    y, sr = librosa.load(instrumental_path)
    
    # Use harmonic separation to ignore drums/percussion
    y_harmonic = librosa.effects.harmonic(y)
    chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
    
    # Define templates for Major and Minor chords
    maj_template = np.array([1,0,0,0,1,0,0,1,0,0,0,0])
    min_template = np.array([1,0,0,1,0,0,0,1,0,0,0,0])
    
    chord_templates = []
    chord_names = []
    roots = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    for i in range(12):
        chord_templates.append(np.roll(maj_template, i))
        chord_names.append(f"{roots[i]} Maj")
    for i in range(12):
        chord_templates.append(np.roll(min_template, i))
        chord_names.append(f"{roots[i]} min")

    chord_templates = np.array(chord_templates)
    matches = np.dot(chord_templates, chroma)
    best_matches = np.argmax(matches, axis=0)
    
    times = librosa.frames_to_time(np.arange(len(best_matches)), sr=sr)
    chord_timeline = []
    last_chord = None
    
    for i, chord_idx in enumerate(best_matches):
        current_chord = chord_names[chord_idx]
        if current_chord != last_chord:
            chord_timeline.append({
                "time": round(float(times[i]), 3),
                "chord": current_chord
            })
            last_chord = current_chord

    with open(output_filename, 'w') as f:
        json.dump(chord_timeline, f, indent=4)
    
    print(f"✓ Success: Saved {output_filename}")
    print(f"Detected {len(chord_timeline)} chord changes.")
    return chord_timeline

# --- MAIN EXECUTION BLOCK ---

def melody_main(original_audio_path, v_test_path):
    print("Initializing Stage 2 Test (30 Second Trim)...")

    # Ensure paths exist
    # original_audio_path = "inputs/vocals.wav"
    # v_test_path = "v_test_30s.wav"
    # i_test_path = "i_test_30s.wav"

    if not os.path.exists("mid-files"):
        os.makedirs("mid-files")

    BASE_DIR = Path(__file__).parent.parent

    # Define the MIDI directory
    MIDI_DIR = BASE_DIR / "mid-files"
    MIDI_DIR.mkdir(parents=True, exist_ok=True)
    new_mid_path = MIDI_DIR / f"{original_audio_path.stem}.mid"

    try:
        # 1. TRIMMING STEP
        if os.path.exists(original_audio_path):
            # print(f"Reading {original_audio_path}...")
            y_30s, sr = librosa.load(original_audio_path, offset=60, duration=30)        
            # sf.write(v_test_path, y_30s, sr)
            # sf.write(i_test_path, y_30s, sr) 
        else:
            print(f"Error: {original_audio_path} not found. Please place a file there.")
            exit()
        
        # 2. RUN EXTRACTION
        melody_file = extract_melody(v_test_path, new_mid_path)
        # chord_data = extract_chords(i_test_path)
        
        # # 3. SUMMARY
        # print("\n" + "="*30)
        # print("EXTRACTION COMPLETE")
        # print("="*30)
        # # print(f"First 5 Chords: {[c['chord'] for c in chord_data[:5]]}")
        # print(f"MIDI File: {os.path.abspath(melody_file)}")
        # print(f"JSON File: {os.path.abspath('chords.json')}")

    except Exception as e:
        print(f"\nError during execution: {e}")
    
    return melody_file
    
    # finally:
        # CLEANUP: Remove the temporary 30s wav files
        # for f in [v_test_path, i_test_path]:
        # for f in [v_test_path]:
        #     if os.path.exists(f):
        #         # os.remove(f)
        #         print(f"Cleaned up {f}")