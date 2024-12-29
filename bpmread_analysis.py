import librosa
import numpy as np
from librosa.feature.rhythm import tempo

from bpmread_logger import logger
from bpmread_model import Analysis


class Analyzer:

    @staticmethod
    def __load_config(config: Analysis):
        if not config.loaded:
            logger.debug(f"Open file {config.path}")
            config.y, config.sr = librosa.load(config.path, sr=None)
            logger.debug(f"Apply harmonic-percussive source separation for {config.path}")
            _, config.y_percussive = librosa.effects.hpss(config.y)
            logger.debug(f"Compute onset envelope for {config.path}")
            config.onset_env = librosa.onset.onset_strength(y=config.y_percussive,
                                                            sr=config.sr,
                                                            hop_length=config.hop_length,
                                                            aggregate=np.median)
            config.loaded = True

    @staticmethod
    def estimate_tempo(config: Analysis) -> float:
        Analyzer.__load_config(config)
        logger.debug(f"Estimating tempo for {config.path}")
        calculated_tempo = tempo(onset_envelope=config.onset_env,
                                 sr=config.sr,
                                 start_bpm=config.start_bpm,
                                 hop_length=config.hop_length,
                                 aggregate=np.median)
        if isinstance(calculated_tempo, np.ndarray):
            calculated_tempo = calculated_tempo[0]  # Extract the first tempo value if it's an array
        logger.info(f"Estimated Tempo of {config.path}: {calculated_tempo:.2f} BPM")
        # noinspection PyTypeChecker
        # checked before
        return calculated_tempo

    @staticmethod
    def analyse_beats(config: Analysis) -> tuple[float, np.ndarray, int]:
        Analyzer.__load_config(config)
        estimated_tempo = Analyzer.estimate_tempo(config)
        logger.debug(f"Analyzing beats {config.path}")
        calculated_tempo, beat_frames = librosa.beat.beat_track(onset_envelope=config.onset_env,
                                                                sr=config.sr,
                                                                hop_length=config.hop_length,
                                                                start_bpm=estimated_tempo,
                                                                tightness=config.tightness)
        if isinstance(calculated_tempo, np.ndarray):
            calculated_tempo = calculated_tempo[0]  # Extract the first element if tempo is an array
        logger.info(f"Analysis of {config.path} completed - (Tempo={calculated_tempo:.2f} BPM)")
        return calculated_tempo, beat_frames, config.sr
