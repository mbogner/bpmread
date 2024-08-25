#!/usr/bin/env python
import argparse

import librosa
import numpy as np

import DaVinciResolveScript
from bpmread_analysis import analyse_beats
from bpmread_logger import logger
from bpmread_model import AudioClip


class BeatMarker:
    resolve = DaVinciResolveScript.scriptapp("Resolve")
    project = resolve.GetProjectManager().GetCurrentProject()

    @staticmethod
    def remove_all_markers(clip_name: str, marker_color: str):
        audio_clip: AudioClip = BeatMarker.__find_clip_by_name(clip_name)
        BeatMarker.__remove_all_markers(audio_clip.davinci_clip, marker_color)
        logger.info(f"Removed all {marker_color} markers from clip {clip_name}")

        # Refresh the Fairlight page to ensure markers are removed
        BeatMarker.__refresh_fairlight_page()

    @staticmethod
    def add_markers(clip_name: str, marker_color: str):
        audio_clip: AudioClip = BeatMarker.__find_clip_by_name(clip_name)
        tempo, frame_list = BeatMarker.__beat_infos(audio_clip.path, audio_clip.davinci_clip)
        BeatMarker.__remove_all_markers(audio_clip.davinci_clip, marker_color)

        for frame in frame_list:
            frame_added = audio_clip.davinci_clip.AddMarker(frame, marker_color, f"Marker at frame {frame}",
                                                            f"Auto-added marker at frame {frame}", 1)
            if frame_added:
                logger.debug(f"Added {marker_color} marker to {audio_clip.name} at frame:{frame}")
            else:
                logger.error(f"Failed to add {marker_color} marker at FrameId:{frame}")

        logger.info(f"Done, tempo={tempo}")

        # Refresh the Fairlight page to ensure markers are visible
        BeatMarker.__refresh_fairlight_page()

    @staticmethod
    def __beat_infos(path: str, davinci_clip) -> tuple[float, list[int]]:
        """
        Returns the tempo and frame list for detected beats in an audio file.
        Enhanced with additional preprocessing and onset detection techniques.
        """
        try:
            tempo, beat_frames, sr = analyse_beats(path)

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
        BeatMarker.resolve.OpenPage("fairlight")
        if not BeatMarker.project:
            raise RuntimeError("No project is loaded")

        # Get the media pool
        media_pool = BeatMarker.project.GetMediaPool()
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
        audio_clips = BeatMarker.__filter_audio_clips(BeatMarker.__load_all_clips())
        for audio_clip in audio_clips:
            if audio_clip.name.lower() == clip_name.lower():
                logger.debug(f'Found clip by name {clip_name}: {audio_clip}')
                return audio_clip
        raise RuntimeError(f'No clip with name {clip_name} found in DaVinci')

    @staticmethod
    def __refresh_fairlight_page():
        # Switch between pages to refresh
        BeatMarker.resolve.OpenPage("edit")
        BeatMarker.resolve.OpenPage("fairlight")

        # Explicitly set the current timeline to ensure refresh
        project = BeatMarker.resolve.GetProjectManager().GetCurrentProject()
        current_timeline = project.GetCurrentTimeline()
        project.SetCurrentTimeline(current_timeline)


def parse_arguments() -> tuple[str, str, str]:
    parser = argparse.ArgumentParser(description="Handle markers in DaVinci Resolve.")
    parser.add_argument('--clip', type=str, help='Clip name', required=True)
    parser.add_argument('--color', type=str, help='Marker color', required=False, default='Yellow')
    parser.add_argument('--command', type=str, help='What to do', required=False, default='add')
    parsed = parser.parse_args()
    return parsed.command, parsed.clip, parsed.color


if __name__ == "__main__":
    _command, _clip, _color = parse_arguments()
    _command = _command.lower()
    if _command == 'add':
        BeatMarker().add_markers(_clip, _color)
    elif _command == 'remove':
        BeatMarker().remove_all_markers(_clip, _color)
