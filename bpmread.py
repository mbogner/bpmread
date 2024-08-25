import argparse
import os

import librosa

from bpmread_config import Config
from bpmread_logger import logger
from bpmread_model import ImportFile


class App:
    input_files: list[ImportFile]

    def __init__(self, input_files: list[ImportFile]):
        self.input_files = input_files

    def run(self):
        for input_file in self.input_files:
            logger.info(f"process {input_file}")
            audio_file = librosa.load(input_file.path)
            y, sr = audio_file
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)  # second result is beat_frames
            bpm = f'{tempo[0]:.2f}'
            with open(f'{input_file.path}.bpm.yml', 'w') as file:
                file.write(f"""result:
  - name: {input_file.name}
    extension: {input_file.ext}
    bpm: {bpm}
""")
            logger.debug(f'processed {input_file}')


def main():
    logger.info(f"starting {Config.APP_NAME}, v{Config.APP_VERSION}, environment: {Config.APP_ENVIRONMENT}")
    App(parse_arguments()).run()


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
