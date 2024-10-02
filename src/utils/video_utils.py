import subprocess
from moviepy.editor import VideoFileClip
import re
import json
import subprocess

def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)
    video.close()

def merge_audio_tracks(input_file, output_file):
    """Merge audio tracks from a video."""
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'copy',
        '-filter_complex', 'amerge',
        '-c:a', 'aac',
        '-b:a', '256k',
        output_file
    ]
    subprocess.run(cmd, check=True)
    return output_file

def split_video(input_file, output_dir, start_seconds, duration, output_file):
    """Split video into segments based on the start time and duration."""
    cmd = [
        'ffmpeg',
        '-ss', str(start_seconds),
        '-i', input_file,
        '-t', str(duration),
        '-c', 'copy',
        output_file
    ]
    subprocess.run(cmd, check=True)

def parse_segments(segment_file):
    """Parse JSON file into a list of segments."""
    with open(segment_file, 'r') as file:
        data = file.read()
    
    # Find all JSON objects in the text
    json_objects = re.findall(r'\{.*?\}', data, re.DOTALL)
    segments = []
    for obj_str in json_objects:
        try:
            obj = json.loads(obj_str)
            segments.append(obj)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON object: {e}")
            continue
    return segments

def convert_to_9_16(input_file, output_file):
    info = get_video_info(input_file)
    width = int(info['streams'][0]['width'])
    height = int(info['streams'][0]['height'])

    target_width, target_height = 1080, 1920
    scale_factor = min(target_width / width, target_height / height)
    scaled_width = int(width * scale_factor)
    scaled_height = int(height * scale_factor)

    pad_x = (target_width - scaled_width) // 2
    pad_y = (target_height - scaled_height) // 2

    filter_complex = f'scale={scaled_width}:{scaled_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:{pad_x}:{pad_y}:color=black'
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-vf', filter_complex,
        '-c:a', 'copy',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-crf', '23',
        output_file
    ]

    subprocess.run(cmd, check=True)

def get_video_info(input_file):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', input_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)


def count_audio_streams(input_file):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', input_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse the JSON output
    data = json.loads(result.stdout)
    
    # Count audio streams
    audio_streams = [stream for stream in data['streams'] if stream['codec_type'] == 'audio']
    return len(audio_streams)

def add_subtitles(input_video, subtitle_file, output_video, subtitle_format="srt"):
    
    options = {
        "align": "2",
        "font_name": "MADE TOMMY",
        "font_size": "15",
        "margin_v": 70,
    }

    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_video,
        "-vf", f"subtitles={subtitle_file}:force_style='Alignment={options['align']},Fontname={options['font_name']},Fontsize={options['font_size']},MarginV={options['margin_v']}'",
        output_video
    ]

    subprocess.run(ffmpeg_cmd, check=True)
