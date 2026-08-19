import wavio as wv
import numpy as np
from pynput.keyboard import Listener as KeyboardListener
import sounddevice as sd



freq = 44100
is_recording = False
recorded_chunks = []

def on_press(key):
    global freq, duration, is_recording
    try:
        if key.char == 'q' and not is_recording:
            is_recording = True
            recorded_chunks.clear()
            sd.InputStream(samplerate=freq, channels=1, dtype='int16', callback=callback).start()
            print("Recording started. Release 'q' to stop")
    except AttributeError:
        pass

def callback(indata, frames, time, status):
    global is_recording
    global recorded_chunks
    if status:
        print(status)
    if is_recording:
        recorded_chunks.append(indata.copy())
        
        
def on_release(key):
    global freq, duration, is_recording
    try:
        if key.char == 'q':
            is_recording = False
            sd.stop()
            full_record = np.concatenate(recorded_chunks)
            wv.write("output.wav", full_record, freq, sampwidth=2)
            print("Recording stopped.")
    except AttributeError:
        pass

    
keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)

keyboard_listener.start()
keyboard_listener.join()
        