import numpy as np
import librosa
import soundfile as sf
from basic_pitch.inference import predict
import json
import os
import pretty_midi

def extract_melody(vocal_path, output_filename='mil_dreams.mid', bpm=120):
    """Extracts MIDI from vocals and applies volume/CC fixes."""
    print(f"\n--- Stage 2A: Processing Melody from {vocal_path} ---")
    # Run Basic Pitch inference
    _, midi_data, _ = predict(vocal_path)

    for instrument in midi_data.instruments:
        # # Fix 1: Normalize Velocity (Note Loudness)
        for note in instrument.notes:
            note.velocity = 100
        
        # Fix 2: Maximize Main Volume (CC 7)
        cc_volume = pretty_midi.ControlChange(number=7, value=127, time=0)
        instrument.control_changes.append(cc_volume)
        
        # Fix 3: Maximize Expression (CC 11)
        cc_expression = pretty_midi.ControlChange(number=11, value=127, time=0)
        instrument.control_changes.append(cc_expression)

    # Save the repaired MIDI file
    midi_data.write(output_filename)
    print(f"✓ Success: Saved {output_filename}")
    return output_filename

def extract_chords(instrumental_path, output_filename='chords.json'):
    """Analyzes harmonic content to identify major/minor chords."""
    print(f"\n--- Stage 2B: Processing Chords from {instrumental_path} ---")
    
    y, sr = librosa.load(instrumental_path)
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

    # Paths
    # Note: Ensure this file path is correct on your machine
    original_audio_path = "inputs/vocals.wav"
    v_test_path = "v_test_30s.wav"
    i_test_path = "i_test_30s.wav"

    try:
        # 1. TRIMMING STEP
        print(f"Reading {original_audio_path}...")
        # Load 30s. Offset is optional (e.g., offset=45 to skip intro)
        y_30s, sr = librosa.load(original_audio_path, offset=60, duration=30)        
        # Save trimmed files to disk for processing functions
        sf.write(v_test_path, y_30s, sr)
        sf.write(i_test_path, y_30s, sr) # Placeholder until Stage 1 separation is ready
        
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