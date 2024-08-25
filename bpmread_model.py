from dataclasses import dataclass


@dataclass(frozen=True)
class ImportFile:
    path: str
    name: str
    ext: str
