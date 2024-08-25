# BPM Read

A simple Python-based tool to analyze beats per minute (BPM) from songs and automatically add or remove beat markers in
DaVinci Resolve.

## Setup

First, clone the project via git and navigate into the created directory:

```shell
git clone git@github.com:mbogner/bpmread.git
cd bpmread
```

It is recommended to use a Python virtual environment. This can be created by:

```shell
python3 -m venv venv
```

Activate the virtual environment with:

```shell
source venv/bin/activate
```

Ensure the virtual environment is activated whenever you work on the project.

## Installation

With the virtual environment activated, install the required packages:

```shell
pip install -r requirements.txt
```

If you encounter an outdated pip warning, update pip with:

```shell
pip install --upgrade pip
```

## Usage

### bpmread Script

The `bpmread.py` script calculates the BPM of audio files. To run the script, use:

```shell
python3 bpmread.py
```

After running the script, you will see a usage message. Follow the instructions provided.

After a successful run, a `<input_file>.bpm.json` file will be generated next to each input file.

#### Sample Usage

To run the script with multiple input files:

```shell
#!/usr/bin/env bash
source venv/bin/activate

python3 bpmread.py --input_file \
  test/test_input1.wav test/test_input1.mp3 \
  test/test_input2.wav test/test_input2.mp3
```

This command will generate four `.bpm.json` files, one next to each input file. Here is a sample
`test/test_input1.wav.bpm.json`:

```json
{
  "file": {
    "path": "test/test_input1.mp3",
    "name": "test_input1",
    "ext": ".mp3"
  },
  "bpm": 92.28515625,
  "beat_frames": [
    28,
    52,
    78,
    106,
    6354,
    6380,
    6408
  ]
}
```

(Note: Most beat frames in the sample response were removed for readability.)

### BeatMarker Script

The `BeatMarker` script allows for automatic addition or removal of beat markers in DaVinci Resolve based on the
detected beats of an audio file.

#### Running the Script

1. **Prepare Your DaVinci Resolve Project**:
    - Open DaVinci Resolve and load your project.
    - Ensure the audio clip you want to analyze is in the Media Pool's root bin.

2. **Run the BeatMarker Script**:

   Open a terminal in the project directory and run:

   ```shell
   python beatmarker.py --clip "your davinci clip name" --color "Yellow" --command "add"
   ```

    - Replace `"Your Clip Name"` with the actual name of your audio clip in DaVinci Resolve.
    - Use `--color` to specify the color of markers (default is "Yellow").
    - Use `--command` to specify the action (`add` to add markers, `remove` to remove them).

#### Example Commands

- **Add Markers**:
    ```shell
    python beatmarker.py --clip "MyAudioClip" --color "Green" --command "add"
    ```
- **Remove Markers**:
    ```shell
    python beatmarker.py --clip "MyAudioClip" --color "Green" --command "remove"
    ```

## Notes

- Ensure the audio clip is named correctly in DaVinci Resolve and matches the `--clip` parameter.
- The script assumes you have access to the DaVinci Resolve Python API through `DaVinciResolveScript`.
- The audio file must be accessible from the script's execution environment.

## Troubleshooting

- **No audio clip found**: Make sure the audio clip is in the Media Pool's root bin.
- **Failed to add markers**: Verify the clip name and ensure DaVinci Resolve is properly configured for scripting.

## License

This project is licensed under the MIT License. See the [LICENSE.txt](LICENSE.txt) file for details.

## Acknowledgments

- [librosa](https://librosa.org/) for audio processing.
- DaVinci Resolve for providing a powerful scripting API.
