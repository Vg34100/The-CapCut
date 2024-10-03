import os
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
    # Count audio streams
    num_audio_streams = count_audio_streams(input_file)
    print(f"Number of audio streams: {num_audio_streams}")

    if num_audio_streams <= 1:
        print("Video has 0 or 1 audio stream. No merging needed.")
        return input_file

    # Construct FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'copy',
        '-filter_complex', f'amerge=inputs={num_audio_streams}',
        '-c:a', 'aac',
        '-b:a', '256k',
        output_file
    ]

    # Run FFmpeg command
    subprocess.run(cmd, check=True)
    print(f"Audio tracks merged. Output saved as {output_file}")
    return output_file

def time_to_seconds(time_str):
    """Convert time string to seconds, handling both dot and comma as decimal separators."""
    time_str = time_str.replace(',', '.')  # Replace comma with dot for proper float conversion
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h = '0'
        m, s = parts
    else:
        raise ValueError(f"Invalid time format: {time_str}")
    return int(h) * 3600 + int(m) * 60 + float(s)

def split_video(input_file, output_dir, segments):
    """Split video into segments based on given timeframes."""
    os.makedirs(output_dir, exist_ok=True)
    
    for i, segment in enumerate(segments):
        timestamp = segment['timestamp']
        start_str, end_str = timestamp.strip('[]').split(' --> ')
        start_seconds = time_to_seconds(start_str)
        end_seconds = time_to_seconds(end_str)
        duration = end_seconds - start_seconds
        
        # Ensure duration is less than or equal to 59 seconds
        if duration > 59:
            duration = 59
            end_seconds = start_seconds + duration
            end_str = f"{int(end_seconds//3600):02d}:{int((end_seconds%3600)//60):02d}:{end_seconds%60:.3f}"
        
        output_file = os.path.join(output_dir, f"segment_{i+1}.mp4")
        
        cmd = [
            'ffmpeg',
            '-ss', str(start_seconds),
            '-i', input_file,
            '-t', str(duration),
            '-c', 'copy',  # Use copy mode for speed
            '-avoid_negative_ts', '1',
            output_file
        ]
        
        subprocess.run(cmd, check=True)
        print(f"Created segment {i+1}: {output_file}")
        
        # Save metadata
        with open(os.path.join(output_dir, f"segment_{i+1}_metadata.txt"), 'w') as f:
            f.write(f"Title: {segment.get('title', '')}\n")
            f.write(f"Description: {segment.get('description', '')}\n")
            f.write(f"Content: {segment.get('content', '')}\n")
            f.write(f"Virality Score: {segment.get('virality', '')}\n")

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
