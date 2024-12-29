#!/usr/bin/env python
# usage: bpmread_davinci_resolve.py [-h] --clip CLIP [--color COLOR] [--command COMMAND]
#          [--start-bpm START_BPM] [--tightness TIGHTNESS] [--hop-length HOP_LENGTH]
#
# Automated beat marker creation in DaVinci Resolve Studio.
#
# options:
# -h, --help            show this help message and exit
# --clip CLIP           Name of the audio clip in the MediaPool
# --color COLOR         Marker color (default: Yellow)
# --command COMMAND     "add" to add markers or "remove" to delete markers
# --start-bpm START_BPM
#                       Initial guess for the tempo (BPM, default: 120.0)
# --tightness TIGHTNESS
#                       Tightness parameter for beat tracking (default 100.0)
# --hop-length HOP_LENGTH
#                       Number of samples between successive frames (default: 512)

import argparse

import librosa
import numpy as np

import DaVinciResolveScript
from bpmread_analysis import analyse_beats
from bpmread_logger import logger
from bpmread_model import AudioClip, BeatsOptions


class Beats:
    resolve = DaVinciResolveScript.scriptapp("Resolve")
    if resolve is None:
        raise RuntimeError("Resolve script couldn't be loaded. Is it running?")
    pm = resolve.GetProjectManager()
    project = resolve.GetProjectManager().GetCurrentProject()

    @staticmethod
    def remove_all_markers(options: BeatsOptions):
        audio_clip: AudioClip = Beats.__find_clip_by_name(options.clip)
        Beats.__remove_all_markers(audio_clip.davinci_clip, options.color)
        logger.info(f"Removed all {options.color} markers from clip {options.clip}")

        # Refresh the Fairlight page to ensure markers are removed
        Beats.__refresh_fairlight_page()

    @staticmethod
    def add_markers(options: BeatsOptions):
        audio_clip: AudioClip = Beats.__find_clip_by_name(options.clip)
        tempo, frame_list = Beats.__beat_infos(
            path=audio_clip.path,
            start_bpm=options.start_bpm,
            tightness=options.tightness,
            hop_length=options.hop_length,
            davinci_clip=audio_clip.davinci_clip
        )
        Beats.__remove_all_markers(audio_clip.davinci_clip, options.color)

        logger.info(f"Start adding markers")
        i = 0
        for i, frame in enumerate(frame_list):
            audio_clip.davinci_clip.AddMarker(frame, options.color, f"Beat {frame}",
                                              f"Auto-added marker at frame {frame}", 1)
            if i > 0 and i % 100 == 0:
                logger.info(f"added {i} markers...")

        logger.info(f"Added {i} markers, tempo={tempo}")

        # Refresh the Fairlight page to ensure markers are visible
        Beats.__refresh_fairlight_page()

    @staticmethod
    def __beat_infos(path: str, start_bpm, tightness, hop_length, davinci_clip) -> tuple[float, list[int]]:
        """
        Returns the tempo and frame list for detected beats in an audio file.
        Enhanced with additional preprocessing and onset detection techniques.
        """
        try:
            tempo, beat_frames, sr = analyse_beats(path=path, start_bpm=start_bpm, tightness=tightness,
                                                   hop_length=hop_length)

            # Calculate frame numbers based on the clip's properties
            frame_rate = float(davinci_clip.GetClipProperty("FPS"))
            duration_str = davinci_clip.GetClipProperty("Duration")  # Duration in HH:MM:SS:FF format

            # Parse duration string to get total seconds
            hours, minutes, seconds, frames = map(int, duration_str.split(':'))
            duration_seconds = hours * 3600 + minutes * 60 + seconds + frames / frame_rate

            # Map beat frames to DaVinci Resolve timeline frames
            timeline_frames = librosa.frames_to_time(beat_frames, sr=sr) * frame_rate
            timeline_frames = np.round(timeline_frames).astype(int)

            # Ensure the frames are within the clip's frame range
            total_frames = int(frame_rate * duration_seconds)
            timeline_frames = timeline_frames[timeline_frames < total_frames]

            return float(tempo), timeline_frames.tolist()

        except Exception as e:
            logger.error(f"Error in beat detection: {e}")
            raise RuntimeError(f"Failed to analyze beats for audio file: {path}")
        except FileNotFoundError:
            logger.error(f"Audio file not found: {path}")
            raise
        except librosa.util.exceptions.ParameterError as e:
            logger.error(f"Invalid parameters for librosa: {e}")
            raise

    @staticmethod
    def __remove_all_markers(davinci_clip, marker_color: str):
        davinci_clip.DeleteMarkersByColor(marker_color)

    @staticmethod
    def __filter_audio_clips(all_clips: list):
        audio_clips = []
        for clip in all_clips:
            clip_properties = clip.GetClipProperty()
            if clip_properties.get("Type") != "Audio":
                continue
            found_clip = AudioClip(
                davinci_clip=clip,
                name=clip.GetName(),
                path=clip_properties.get("File Path"),
            )
            audio_clips.append(found_clip)

        if len(audio_clips) < 1:
            raise RuntimeError("No audio clip found in the MediaPool root bin.")

        return audio_clips

    @staticmethod
    def __load_all_clips():
        Beats.resolve.OpenPage("fairlight")
        if not Beats.project:
            raise RuntimeError("No project is loaded")

        # Get the media pool
        media_pool = Beats.project.GetMediaPool()
        root_bin = media_pool.GetRootFolder()

        # Go to the root bin
        media_pool.SetCurrentFolder(root_bin)

        # Get all clips in the root bin
        davinci_clips = root_bin.GetClipList()
        if not davinci_clips or not davinci_clips[0]:
            raise RuntimeError("Error: MediaPool root bin doesn't contain any clips. "
                               "Please add an audio clip and try again!")
        return davinci_clips

    @staticmethod
    def __find_clip_by_name(clip_name: str):
        audio_clips = Beats.__filter_audio_clips(Beats.__load_all_clips())
        available_clips = [clip.name for clip in audio_clips]
        for audio_clip in audio_clips:
            if audio_clip.name.lower() == clip_name.lower():
                logger.debug(f'Found clip by name {clip_name}: {audio_clip}')
                return audio_clip
        raise RuntimeError(f'No clip with name "{clip_name}" found. Available clips: {available_clips}')

    @staticmethod
    def __refresh_fairlight_page():
        # Switch between pages to refresh
        Beats.resolve.OpenPage("edit")
        Beats.resolve.OpenPage("fairlight")

        # Explicitly set the current timeline to ensure refresh
        project = Beats.resolve.GetProjectManager().GetCurrentProject()
        current_timeline = project.GetCurrentTimeline()
        project.SetCurrentTimeline(current_timeline)


def parse_arguments() -> BeatsOptions:
    parser = argparse.ArgumentParser(description="Automated beat marker creation in DaVinci Resolve Studio.")
    parser.add_argument('--clip', type=str, help='Name of the audio clip in the MediaPool', required=True)
    parser.add_argument('--color', type=str, help='Marker color (default: Yellow)', default='Yellow', required=False)
    parser.add_argument('--command', type=str, help='"add" to add markers or "remove" to delete markers', default='add',
                        required=False)
    parser.add_argument('--start-bpm', type=float, help='Initial guess for the tempo (BPM, default: 120.0)',
                        default=120.0, required=False)
    parser.add_argument('--tightness', type=float, help='Tightness parameter for beat tracking (default 100.0)',
                        default=100.0, required=False)
    parser.add_argument('--hop-length', type=int, help='Number of samples between successive frames (default: 512)',
                        default=512, required=False)
    parsed = parser.parse_args()
    return BeatsOptions(
        command=parsed.command.lower(),
        clip=parsed.clip,
        color=parsed.color,
        start_bpm=parsed.start_bpm,
        tightness=parsed.tightness,
        hop_length=parsed.hop_length,
    )


if __name__ == "__main__":
    cliOptions = parse_arguments()
    if cliOptions.command == 'add':
        Beats().add_markers(cliOptions)
    elif cliOptions.command == 'remove':
        Beats().remove_all_markers(cliOptions)
