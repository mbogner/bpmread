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
            return asdict(obj)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


@dataclass(frozen=True)
class AudioClip:
    davinci_clip: Any
    name: str
    path: str
