import subprocess
import os

def add_subtitles(input_video, subtitle_file, output_video, subtitle_format="srt"):
    """
    Adds subtitles to a video using FFmpeg.
    
    :param input_video: Path to the input video file.
    :param subtitle_file: Path to the subtitle file (SRT or ASS).
    :param output_video: Path to the output video file.
    :param subtitle_format: Format of the subtitle file ('srt' or 'ass').
    """
    # Check subtitle format
    if subtitle_format not in ["srt", "ass"]:
        raise ValueError("Unsupported subtitle format. Use 'srt' or 'ass'.")

    # Check if the subtitle file needs to be converted from SRT to ASS
    if subtitle_format == "srt":
        # Convert SRT to ASS if necessary
        ass_subtitle_file = os.path.splitext(subtitle_file)[0] + ".ass"
        convert_cmd = [
            "ffmpeg",
            "-i", subtitle_file,
            ass_subtitle_file
        ]
        subprocess.run(convert_cmd, check=True)
        subtitle_file = ass_subtitle_file

    #  ffmpeg -i input.mp4 -vf subtitles=subtitle.srt output_srt.mp4

    # FFmpeg command to add subtitles
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_video,
        "-vf", f"subtitles={subtitle_file}:force_style='Alignment={options["align"]},Fontname={options['font_name']},Fontsize={options['font_size']},MarginV={options['margin_v']}'" if subtitle_format == "srt" else f"ass={subtitle_file}",
        output_video
    ]

    # Run the FFmpeg command
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Subtitles added successfully! Output saved as {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# Example usage:
input_video = "data/input/test1.mp4"
subtitle_file = "data/temp/audio.srt"  # or "subtitles.ass"
output_video = "data/out/output.mp4"
options = {
    "align": "2",
    "font_name": "Indigo Regular",
    "font_size": "15",
    "margin_v": 70,
}

add_subtitles(input_video, subtitle_file, output_video, subtitle_format="srt")
