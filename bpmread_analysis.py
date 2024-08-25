import librosa
import numpy as np

from bpmread_logger import logger


def analyse_beats(path: str, start_bpm: float = 120.0, tightness: float = 100.0, hop_length: int = 512):
    """
    Analyzes the beats of an audio file and returns the estimated tempo and beat frames.

    Args:
        path (str): Path to the audio file.
        start_bpm (float): Initial guess for the tempo (in beats per minute).
        tightness (float): Tightness parameter for beat tracking. Higher values restrict the beat tracker.
        hop_length (int): Number of samples between successive frames for onset detection.

    Returns:
        tuple: Estimated tempo (float), array of beat frame indices (numpy.ndarray), sample rate (int)
    """
    logger.info(f"Analyzing {path}")

    # Load the audio file
    y, sr = librosa.load(path, sr=None)  # Load audio with native sampling rate

    # Apply a high-pass filter to remove low-frequency noise
    y = librosa.effects.preemphasis(y)

    # Use a harmonic-percussive source separation (HPSS) to focus on percussive elements
    _, y_percussive = librosa.effects.hpss(y)

    # Use the percussive component for beat tracking
    onset_env = librosa.onset.onset_strength(y=y_percussive, sr=sr, hop_length=hop_length, aggregate=np.median)

    # Fine-tune the beat tracking algorithm with flexible parameters
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop_length,
                                                 start_bpm=start_bpm, tightness=tightness)

    if isinstance(tempo, np.ndarray):
        tempo = tempo[0]  # Extract the first element if tempo is an array

    logger.info(f"Analysis of {path} completed. Tempo: {tempo:.2f} BPM")

    return tempo, beat_frames, sr
