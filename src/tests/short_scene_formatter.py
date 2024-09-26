# short_scene_formatter.py
import subprocess
import json

def get_video_info(input_file):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', input_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def convert_to_9_16_fast(input_file, output_file):
    # Get video information
    info = get_video_info(input_file)
    width = int(info['streams'][0]['width'])
    height = int(info['streams'][0]['height'])

    # Set target dimensions
    target_width = 1080
    target_height = 1920

    # Calculate scaling factor
    scale_factor = min(target_width / width, target_height / height)
    scaled_width = int(width * scale_factor)
    scaled_height = int(height * scale_factor)

    # Calculate padding
    pad_x = (target_width - scaled_width) // 2
    pad_y = (target_height - scaled_height) // 2

    # Construct FFmpeg command
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

    # Run FFmpeg command
    subprocess.run(cmd, check=True)

# Example usage
input_file = "data/input/secondary_object.mp4"
output_file = "data/out/output.mp4"
convert_to_9_16_fast(input_file, output_file)