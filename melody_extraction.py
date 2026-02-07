import numpy as np
import librosa
import soundfile as sf
from basic_pitch.inference import predict
import json
import os

def extract_features(vocal_path, instrumental_path):
    # --- Melody Extraction (Basic Pitch) ---
    print(f"--- Stage 2: Processing {vocal_path} ---")
    print("Extracting melody (this may take a moment)...")
    
    # Predict returns: (model_output, midi_data, note_events)
    _, midi_data, _ = predict(vocal_path)
    
    # Save the raw MIDI file
    midi_data.write('melody.mid')
    print("✓ Success: Saved melody.mid")

    # --- Chord detection (Librosa Template Matching) ---
    print(f"\n--- Stage 2: Processing {instrumental_path} ---")
    print("Extracting chords...")
    y, sr = librosa.load(instrumental_path)
    
    y_harmonic = librosa.effects.harmonic(y)
    chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
    
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

    with open('chords.json', 'w') as f:
        json.dump(chord_timeline, f, indent=4)
    
    print("✓ Success: Saved chords.json")
    print(f"Detected {len(chord_timeline)} chord changes.")
    return chord_timeline

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    print("🚀 Initializing Stage 2 Test...")

    # 1. MOCK STAGE 1: Load a built-in example track
    # 'choice' is a clear pop-rock sample included with librosa
    print("Loading internal sample audio to simulate separated stems...")
    example_audio = librosa.example('choice')
    y, sr = librosa.load(example_audio, duration=30) # Test first 30 seconds only for speed
    
    # Use Harmonic/Percussive separation as a "Poor Man's Spleeter" for testing
    y_harm, y_perc = librosa.effects.hpss(y)
    
    # Save these as temporary files
    v_test, i_test = "test_vocals.wav", "test_inst.wav"
    sf.write(v_test, y_harm, sr)
    sf.write(i_test, y_harm, sr) # Using harm for both as a placeholder

    try:
        # 2. RUN STAGE 2
        results = extract_features(v_test, i_test)
        
        # 3. PRINT RESULTS SUMMARY
        print("\n--- Extraction Summary ---")
        print(f"First 5 Chords Detected: {[c['chord'] for c in results[:5]]}")
        print("Test complete. You can now open 'melody.mid' and 'chords.json'!")

    except Exception as e:
        print(f"Error during execution: {e}")
    
    finally:
        # Cleanup temp files if desired
        if os.path.exists(v_test): os.remove(v_test)
        if os.path.exists(i_test): os.remove(i_test)