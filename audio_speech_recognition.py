import json
import os
import sys
import wave

from pydub import AudioSegment
from vosk import Model, KaldiRecognizer
import numpy as np


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


def calculate_raised_voice(segment: AudioSegment, threshold: int = -20) -> bool:
    loudness = segment.dBFS
    return loudness > threshold


def analyze_audio(wav_path):
    check_and_convert_audio(wav_path, wav_path)
    full_audio = AudioSegment.from_file(wav_path, format="wav")
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

                    # duration calc
                    words = result.get("result", [])
                    if words:
                        start_time = words[0]["start"]
                        end_time = words[-1]["end"]
                        duration = round(end_time - start_time)
                    else:
                        duration = 0

                    # raised_voice calc
                    segment_start = int(start_time * 1000)
                    segment_end = int(end_time * 1000)
                    audio_segment = full_audio[segment_start:segment_end]
                    raised_voice = calculate_raised_voice(audio_segment)

                    gender = determine_gender_simple(audio_segment)

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


def determine_gender_simple(audio_segment: AudioSegment) -> str:
    """
    Gender determination based on signal frequency.
    Returns:
        str: 'male', 'female', 'unknown'.
    """
    if len(audio_segment) == 0:
        return "unknown"

    # convert audio to array
    samples = np.array(audio_segment.get_array_of_samples())

    if len(samples) == 0:
        return "unknown"

    # Calculating the spectrum using FFT (fast Fourier transform)
    spectrum = np.fft.fft(samples)
    frequencies = np.fft.fftfreq(len(spectrum), 1 / audio_segment.frame_rate)
    if len(frequencies) == 0 or len(spectrum) == 0:
        return "unknown"

    # leave only positive frequencies
    spectrum = np.abs(spectrum[:len(spectrum) // 2])
    frequencies = frequencies[:len(frequencies) // 2]

    # looking for the dominant frequency
    dominant_frequency = frequencies[np.argmax(spectrum)]

    # low frequency - male voice, high - female
    if dominant_frequency < 300:
        return "male"
    else:
        return "female"


MODEL_PATH = 'vosk-model-small-ru-0.22'
if not os.path.exists(MODEL_PATH):
    print("Please download the model from https://alphacephei.com/vosk/models, unpack and specify MODEL_PATH.")
    sys.exit(1)

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)
recognizer.SetWords(True)
