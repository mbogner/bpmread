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
   python bpmread_davinci_resolve.py --clip "your davinci clip name" --color "Yellow" --command "add"
   ```

    - Replace `"Your Clip Name"` with the actual name of your audio clip in DaVinci Resolve.
    - Use `--color` to specify the color of markers (default is "Yellow").
    - Use `--command` to specify the action (`add` to add markers, `remove` to remove them).

#### Example Commands

- **Add Markers**:
    ```shell
    python bpmread_davinci_resolve.py --clip "MyAudioClip" --color "Green" --command "add"
    ```
- **Remove Markers**:
    ```shell
    python bpmread_davinci_resolve.py --clip "MyAudioClip" --color "Green" --command "remove"
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

## Distribution

Here is how to create a binary release of this tool.

```shell
pip install pyinstaller
pyinstaller --onefile bpmread_davinci_resolve.py
```

### runner script

#### unix

included as `run_unix.sh`

```shell
#!/bin/bash
chmod +x ./bpmread_davinci_resolve
./bpmread_davinci_resolve "$@"
```

## Advanced Parameters

The chosen defaults for start-bpm, tightness, and hop-length are reasonable for many typical audio tracks, but their
suitability depends on the specific characteristics of the audio you’re analyzing. Here’s a breakdown of each default
and its impact:

### `start-bpm`

- **What it does**:
    - `start-bpm` provides an initial estimate for the tempo. The beat tracking algorithm uses this value as a starting
      point for its analysis.
- **Why 120 BPM is a reasonable default**:
    - 120 BPM is a common tempo in many genres of music (e.g., pop, dance, rock).
    - It serves as a good general-purpose default for a wide range of audio tracks.
- **When to adjust**:
    - If the music is noticeably slower or faster (e.g., classical music at ~60 BPM or electronic music at ~150 BPM),
      you might achieve better results by tuning this value closer to the expected tempo.
- **Alternative approach**:
    - Leave `start-bpm` unspecified (`None`) to let the algorithm estimate the tempo dynamically, though this may take
      slightly more processing time.

### `tightness`

- **What it does**:
    - `tightness` controls how strictly the beat tracker adheres to the `start-bpm` estimate.
    - A higher value forces the tracker to prioritize consistency with `start-bpm`, while a lower value allows more
      flexibility.
- **Why 100.0 is a reasonable default**:
    - This value balances flexibility and consistency for most general-purpose audio.
    - It ensures the algorithm does not stray too far from the expected tempo while accommodating natural variations in
      tempo.
- **When to adjust**:
    - **Increase (e.g., 200–300)**:
        - If the audio has a steady tempo, such as in electronic music or metronomic tracks.
    - **Decrease (e.g., 50–75)**:
        - If the audio has a lot of tempo variation, such as live performances or jazz.

### `hop-length`: 512

- **What it does**:
    - `hop-length` defines the number of audio samples between successive frames analyzed by the algorithm.
    - It determines the temporal resolution of the analysis.
- **Why 512 is reasonable**:
    - It provides a good trade-off between temporal resolution and computational efficiency for most audio sampled at
      44.1 kHz or 48 kHz.
    - At a sampling rate of 44.1 kHz, a hop length of 512 corresponds to a frame duration of ~11.6 ms, which is
      sufficient for detecting beats in most music.
- **When to adjust**:
    - **Increase (e.g., 1024–2048)**:
        - For longer audio files or low-tempo music where computational efficiency is important.
    - **Decrease (e.g., 256)**:
        - For high-tempo music or audio with rapid rhythmic changes, where finer resolution is needed.

### Recommended Adjustments Based on Use Case

| Use Case                  | `start-bpm` | `tightness` | `hop-length` |
|---------------------------|-------------|-------------|--------------|
| **Pop/Dance/Rock**        | 120.0       | 100.0       | 512          |
| **Electronic/EDM**        | 140.0       | 200.0       | 512          |
| **Classical**             | 60.0        | 75.0        | 1024         |
| **Jazz/Live Performance** | 90.0        | 50.0        | 256          |
| **General Purpose**       | 120.0       | 100.0       | 512          |
