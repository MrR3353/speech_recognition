import json
import os
import sys
import wave

from pydub import AudioSegment
from vosk import Model, KaldiRecognizer


def convert_mp3_to_wav(mp3_path):
    audio = AudioSegment.from_mp3(mp3_path)
    wav_path = mp3_path.replace(".mp3", ".wav")
    audio.export(wav_path, format="wav")
    return wav_path


def check_and_convert_audio(input_file: str, output_file: str):
    """
    Checks the audio file for compliance with VOSK requirements
    (must be WAV format mono PCM with sample rate 16000) and converts it if necessary
    """
    try:
        with wave.open(input_file, "rb") as wf:
            if wf.getnchannels() == 1 and wf.getsampwidth() == 2 and wf.getframerate() == 16000:
                return input_file
    except wave.Error:
        raise wave.Error("The file is not a WAV, or cannot be opened using the standard method.")

    audio = AudioSegment.from_file(input_file)
    audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    audio.export(output_file, format="wav")
    return output_file


def analyze_audio(wav_path):
    check_and_convert_audio(wav_path, wav_path)
    with wave.open(wav_path, "rb") as wf:
        dialog = []
        source_toggle = True  # Simulates "receiver" and "transmitter"
        durations = {"receiver": 0, "transmitter": 0}
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if "text" in result and result["text"].strip():
                    source = "receiver" if source_toggle else "transmitter"
                    source_toggle = not source_toggle
                    duration = len(result["text"].split())  # Simulated duration
                    raised_voice = any(word.isupper() for word in result["text"].split())
                    gender = "male" if source_toggle else "female"

                    dialog.append({
                        "source": source,
                        "text": result["text"],
                        "duration": duration,
                        "raised_voice": raised_voice,
                        "gender": gender
                    })
                    durations[source] += duration

    return {
        "dialog": dialog,
        "result_duration": durations
    }


MODEL_PATH = 'vosk-model-small-ru-0.22'
if not os.path.exists(MODEL_PATH):
    print("Please download the model from https://alphacephei.com/vosk/models, unpack and specify MODEL_PATH.")
    sys.exit(1)

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)
recognizer.SetWords(True)
