# bpmread

Simple python based tool to get beats per minute (BPM) from a song. It was tested with .mp3 and .wav files.

## Setup

First checkout the project via git and change into the created directory

```shell
git clone git@github.com:mbogner/bpmread.git
cd bpmread
```

It is recommended to use a python virtual environment.

This can be created by

```shell
python3 -m venv venv
```

and then activated by

```shell
source venv/bin/activate
```

Make sure to always work inside your virtual environment which means having it activated before doing something.

## Installation

With the venv activated you can then install the requirements by

```shell
pip install -r requirements.txt
```

In case it complains about an outdated pip run

```shell
pip install --upgrade pip
```

## Usage

The script then can be run

```shell
python3 bpmread.py
```

This will greet you with a usage message. Please read it.

After successful run there will be a `<input_file>.bpm.yml` file next to each input file.

### Sample

The following sample shows how to run the script with multiple input files

```shell
#!/usr/bin/env bash
source venv/bin/activate

python3 bpmread.py --input_file \
  test/test_input1.wav test/test_input1.mp3 \
  test/test_input2.wav test/test_input2.mp3
```

Results in 4 .bpm.yml files. One next to each input file. Here is the sample `test/test_input1.wav.bpm.yml`:

```yaml
result:
  - name: test_input1
    extension: .wav
    bpm: 92.29
```