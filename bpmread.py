import argparse
import json
import os

from bpmread_analysis import analyse_beats
from bpmread_config import Config
from bpmread_logger import logger
from bpmread_model import ImportFile, FileMarker


class BPMRead:
    input_files: list[ImportFile]

    def __init__(self, input_files: list[ImportFile]):
        self.input_files = input_files

    def run(self):
        for input_file in self.input_files:
            logger.info(f"process {input_file.path}")
            tempo, beat_frames, _ = analyse_beats(input_file.path)
            file_marker = FileMarker(
                file=input_file,
                bpm=float(tempo),
                beat_frames=beat_frames.tolist(),
            )
            with open(f'{input_file.path}.bpm.json', 'w') as file:
                json_str = json.dumps(file_marker, default=FileMarker.file_marker_to_dict, indent=2)
                file.write(json_str)
            logger.debug(f'processed {input_file.path}')


def main():
    logger.info(f"starting {Config.APP_NAME}, v{Config.APP_VERSION}, environment: {Config.APP_ENVIRONMENT}")
    BPMRead(parse_arguments()).run()


def parse_arguments() -> list[ImportFile]:
    parser = argparse.ArgumentParser(description="Tool to read beats per minute from a song.")
    # works: --input_file test/test_input1.mp3 test/test_input1.wav
    # does not work: --input_file test/test_input1.mp3 --input_file test/test_input1.wav
    parser.add_argument('--input_file', type=str, help='input file', required=True, nargs='+')
    args = parser.parse_args()
    return parse_input_files(args.input_file)


def parse_input_files(arguments) -> list[ImportFile]:
    input_files: list[ImportFile] = []
    for input_file in arguments:
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f'file does not exist: {input_file}')
        file_name, file_extension = os.path.splitext(input_file)
        file_name = file_name.split(os.sep)[-1]
        input_files.append(ImportFile(path=input_file, name=file_name, ext=file_extension))
    return input_files


if __name__ == "__main__":
    main()
