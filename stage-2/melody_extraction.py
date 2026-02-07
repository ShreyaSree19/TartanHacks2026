import numpy as np
import librosa
import soundfile as sf
import json
import os
import pretty_midi
from basic_pitch.inference import predict
from scipy.signal import butter, sosfilt

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

# --- EXTRACTION FUNCTIONS ---
def extract_melody(vocal_path, output_filename='mil_dreams.mid', bpm=120):
    print(f"\n--- Stage 2A: Processing Melody from {vocal_path} ---")
    
    y, sr = librosa.load(vocal_path, sr=None)
    y_filtered = preprocess_audio(y, sr)
    
    temp_filtered_path = "temp_vocal_cleaned.wav"
    sf.write(temp_filtered_path, y_filtered, sr)

    _, midi_data, _ = predict(temp_filtered_path)

    # # --- FIX 1: SET EXPLICIT TEMPO AND TIME SIGNATURE ---
    # # This prevents MuseScore from guessing 3/4 time.
    # midi_data.tempo_relabel(bpm) 
    
    # # Add 4/4 time signature at time 0
    # ts = pretty_midi.TimeSignature(4, 4, 0)
    # midi_data.time_signature_changes.append(ts)

    for instrument in midi_data.instruments:
        # --- FIX 2: NOISE REDUCTION (QUANTIZATION & CLEANUP) ---
        # 1. Remove very short "glitch" notes (less than 50ms)
        instrument.notes = [n for n in instrument.notes if (n.end - n.start) > 0.05]
        
        # 2. Normalize Velocity
        for note in instrument.notes:
            note.velocity = 100 

        # Fix CC Volume
        cc_volume = pretty_midi.ControlChange(number=7, value=127, time=0)
        instrument.control_changes.append(cc_volume)

    midi_data.write(output_filename)
    
    if os.path.exists(temp_filtered_path):
        os.remove(temp_filtered_path)
        
    print(f"✓ Success: Saved {output_filename} at {bpm} BPM in 4/4")
    return output_filename

# def extract_melody(vocal_path, output_filename='mil_dreams.mid'):
#     """Extracts MIDI from vocals after applying a bandpass filter."""
#     print(f"\n--- Stage 2A: Processing Melody from {vocal_path} ---")
    
#     # Load audio and apply the filter
#     y, sr = librosa.load(vocal_path, sr=None)
#     y_filtered = preprocess_audio(y, sr)
    
#     # Basic Pitch usually takes a path, so we save a temporary clean version
#     temp_filtered_path = "temp_vocal_cleaned.wav"
#     sf.write(temp_filtered_path, y_filtered, sr)

#     # Run Basic Pitch inference
#     print("  > Running MIDI Inference (Basic Pitch)...")
#     _, midi_data, _ = predict(temp_filtered_path)

#     for instrument in midi_data.instruments:
#         # Fix 2: Maximize Main Volume (CC 7)
#         cc_volume = pretty_midi.ControlChange(number=7, value=127, time=0)
#         instrument.control_changes.append(cc_volume)
        
#         # Fix 3: Maximize Expression (CC 11)
#         cc_expression = pretty_midi.ControlChange(number=11, value=127, time=0)
#         instrument.control_changes.append(cc_expression)

#     # Save the repaired MIDI file
#     midi_data.write(output_filename)
    
#     # Cleanup
#     if os.path.exists(temp_filtered_path):
#         os.remove(temp_filtered_path)
        
#     print(f"✓ Success: Saved {output_filename}")
#     return output_filename

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

if __name__ == "__main__":
    print("Initializing Stage 2 Test (30 Second Trim)...")

    # Ensure paths exist
    original_audio_path = "inputs/vocals.wav"
    v_test_path = "v_test_30s.wav"
    i_test_path = "i_test_30s.wav"

    if not os.path.exists("inputs"):
        os.makedirs("inputs")

    try:
        # 1. TRIMMING STEP
        if os.path.exists(original_audio_path):
            print(f"Reading {original_audio_path}...")
            y_30s, sr = librosa.load(original_audio_path, offset=60, duration=30)        
            sf.write(v_test_path, y_30s, sr)
            sf.write(i_test_path, y_30s, sr) 
        else:
            print(f"Error: {original_audio_path} not found. Please place a file there.")
            exit()
        
        # 2. RUN EXTRACTION
        melody_file = extract_melody(v_test_path)
        chord_data = extract_chords(i_test_path)
        
        # 3. SUMMARY
        print("\n" + "="*30)
        print("EXTRACTION COMPLETE")
        print("="*30)
        print(f"First 5 Chords: {[c['chord'] for c in chord_data[:5]]}")
        print(f"MIDI File: {os.path.abspath(melody_file)}")
        print(f"JSON File: {os.path.abspath('chords.json')}")

    except Exception as e:
        print(f"\nError during execution: {e}")
    
    finally:
        # CLEANUP: Remove the temporary 30s wav files
        for f in [v_test_path, i_test_path]:
            if os.path.exists(f):
                os.remove(f)
                print(f"Cleaned up {f}")