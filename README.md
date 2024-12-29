# BPM Read

The script `bpmread_davinci_resolve` allows for automatic addition or removal of beat markers in DaVinci Resolve
based on the detected beats of an audio file.

It only works with Studio version because free version doesn't support scripting.

```
usage: bpmread_davinci_resolve [-h] --clip CLIP [--color COLOR] [--command COMMAND]
          [--start-bpm START_BPM] [--tightness TIGHTNESS] [--hop-length HOP_LENGTH]

Automated beat marker creation in DaVinci Resolve Studio.

options:
-h, --help                    show this help message and exit
--clip CLIP                  Name of the audio clip in the MediaPool
--color COLOR           Marker color (default: Yellow)
--command COMMAND    
                                     "add" to add markers or "remove" to delete markers
--start-bpm START_BPM
                                     Initial guess for the tempo (BPM, default: 120.0)
--tightness TIGHTNESS
                                     Tightness parameter for beat tracking (default 100.0)
 --hop-length HOP_LENGTH
                                     Number of samples between successive frames (default: 512)
```

You can download the binary for mac arm64 under the [release section](https://github.com/mbogner/bpmread/releases).

## Running the Script

1. **Prepare Your DaVinci Resolve Project**:
    - Open DaVinci Resolve and load your project.
    - Ensure the audio clip you want to analyze is in the Media Pool's root bin.

2. **Run the `bpmread_davinci_resolve` Binary**:

   Open a terminal in the project directory and run:

   ```shell
   bpmread_davinci_resolve --clip "your davinci clip name.mp3"
   ```

    - Replace `"your davinci clip name.mp3"` with the actual name of your audio clip in DaVinci Resolve.

### Further Examples

- **Add Green Markers**:
    ```shell
    bpmread_davinci_resolve --clip "MyAudioClip" --color "Green" --command "add"
    ```
- **Remove Green Markers**:
    ```shell
    bpmread_davinci_resolve --clip "MyAudioClip" --color "Green" --command "remove"
    ```

## Notes

- Ensure the audio clip is named correctly in DaVinci Resolve and matches the `--clip` parameter.
- The script assumes you have access to the DaVinci Resolve Python API through `DaVinciResolveScript`.
- The audio file must be accessible from the script's execution environment.

## Troubleshooting

- **No audio clip found**: Make sure the audio clip is in the Media Pool's root bin.
- **Failed to add markers**: Verify the clip name and ensure DaVinci Resolve is properly configured for scripting.

## Advanced Parameters

The chosen defaults for start-bpm, tightness, and hop-length are reasonable for many typical audio tracks, but their
suitability depends on the specific characteristics of the audio you’re analyzing. Here’s a breakdown of each default
and its impact:

### `start-bpm` (default: 120)

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

### `tightness` (default: 100)

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

### `hop-length` (default: 512)

- **What it does**:
    - `hop-length` defines the number of audio samples between successive frames analyzed by the algorithm.
    - It determines the temporal resolution of the analysis.
- **Why 512 is a reasonable default**:
    - It provides a good trade-off between temporal resolution and computational efficiency for most audio sampled at
      44.1 kHz or 48 kHz.
    - At a sampling rate of 44.1 kHz, a hop length of 512 corresponds to a frame duration of ~11.6 ms, which is
      sufficient for detecting beats in most music.
- **When to adjust**:
    - **Increase (e.g., 1024–2048)**:
        - For longer audio files or low-tempo music where computational efficiency is important.
    - **Decrease (e.g., 256)**:
        - For high-tempo music or audio with rapid rhythmic changes, where finer resolution is needed.

## Recommended Adjustments Based on Use Case

| Use Case                  | `start-bpm` | `tightness` | `hop-length` |
|---------------------------|-------------|-------------|--------------|
| **Pop/Dance/Rock**        | 120.0       | 100.0       | 512          |
| **Electronic/EDM**        | 140.0       | 200.0       | 512          |
| **Classical**             | 60.0        | 75.0        | 1024         |
| **Jazz/Live Performance** | 90.0        | 50.0        | 256          |
| **General Purpose**       | 120.0       | 100.0       | 512          |

## Distribution

Here is how to create a binary release of this tool.

```shell
pyinstaller --onefile bpmread_davinci_resolve.py
```

This requires `pyinstaller`:

```shell
pip install pyinstaller
```