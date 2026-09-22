import wavio as wv
import numpy as np
import threading
from pynput.keyboard import Listener as KeyboardListener
import sounddevice as sd



RECORD_KEY = 'q'

freq = 44100
is_recording = False
recorded_chunks = []
event = threading.Event()
_stream = None


def on_press(key):
    global freq, is_recording, _stream
    try:
        if key.char == RECORD_KEY and not is_recording:
            is_recording = True
            recorded_chunks.clear()
            _stream = sd.InputStream(samplerate=freq, channels=1, dtype='int16', callback=callback)
            _stream.start()
            print(f"Recording started. Release '{RECORD_KEY}' to stop")
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
    global freq, is_recording, _stream
    try:
        if key.char == RECORD_KEY:
            is_recording = False
            if _stream is not None:
                _stream.stop()
                _stream.close()
                _stream = None
            full_record = np.concatenate(recorded_chunks)
            wv.write("output.wav", full_record, freq, sampwidth=2)
            print("Recording stopped.")
            event.set()
    except AttributeError:
        pass


def listen_and_record():
    """ Starts a push-to-talk recording session and returns the audio filename once complete"""
    print(f"Press and hold '{RECORD_KEY}' to talk, release to stop.")
    listener = KeyboardListener(on_press=on_press, on_release=on_release, suppress=True)
    listener.start()
    event.wait()
    event.clear()
    return "output.wav"

if __name__ == "__main__":
    print(f"Testing and listening")
    result = listen_and_record()
    print(f"Got back: {result}")