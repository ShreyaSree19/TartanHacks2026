import pretty_midi

def verify_midi(file_path):
    try:
        pm = pretty_midi.PrettyMIDI(file_path)
        print(f"✅ File Loaded: {file_path}")
        print(f"Duration: {pm.get_end_time():.2f} seconds")
        
        for i, instrument in enumerate(pm.instruments):
            print(f"\nInstrument {i}: {instrument.name}")
            print(f"Number of notes: {len(instrument.notes)}")
            
            if len(instrument.notes) > 0:
                # Check the first note for duration
                n = instrument.notes[0]
                duration = n.end - n.start
                print(f"Sample Note: Pitch={n.pitch}, Start={n.start:.2f}s, Duration={duration:.2f}s")
                
                if duration <= 0:
                    print("⚠️ WARNING: Note has zero or negative duration!")
            else:
                print("⚠️ WARNING: This instrument has no notes!")
                
    except Exception as e:
        print(f"❌ Corrupt File: {e}")

verify_midi('melody.mid')