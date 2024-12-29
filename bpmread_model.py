from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class ImportFile:
    path: str
    name: str
    ext: str


@dataclass(frozen=True)
class FileMarker:
    file: ImportFile
    bpm: float
    beat_frames: list[int]

    @staticmethod
    def file_marker_to_dict(obj):
        if isinstance(obj, FileMarker):
            # noinspection PyTypeChecker
            return asdict(obj)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


@dataclass(frozen=True)
class AudioClip:
    davinci_clip: Any
    name: str
    path: str


@dataclass(frozen=True)
class BeatsOptions:
    clip: str
    command: str = "add"
    color: str = "Yellow"
    start_bpm: float = 120.0
    tightness: float = 100.0
    hop_length: int = 512

    __VALID_COLORS = {"Red", "Yellow", "Green", "Blue", "Cyan", "Magenta", "Pink", "White"}
    __VALID_COMMANDS = {"add", "remove"}

    def __post_init__(self):
        self.validate()

    def validate(self):
        if self.command not in BeatsOptions.__VALID_COMMANDS:
            raise ValueError(f"Invalid command: {self.command}. Valid commands are: {BeatsOptions.__VALID_COMMANDS}")
        if self.color not in BeatsOptions.__VALID_COLORS:
            raise ValueError(f"Invalid marker color: {self.color}. Valid colors are: {BeatsOptions.__VALID_COLORS}")
