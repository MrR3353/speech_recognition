import sys
import os
from vosk import Model, KaldiRecognizer
import pyaudio

# Load the Vosk model
MODEL_PATH = 'vosk-model-small-ru-0.22'
if not os.path.exists(MODEL_PATH):
    print("Please download the model from https://alphacephei.com/vosk/models, unpack and specify MODEL_PATH.")
    sys.exit(1)

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

# Start audio stream
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

print("Listening...")

while True:
    data = stream.read(4000)
    if recognizer.AcceptWaveform(data):
        result = recognizer.Result()
        print(result)
    else:
        partial_result = recognizer.PartialResult()
        print(partial_result)