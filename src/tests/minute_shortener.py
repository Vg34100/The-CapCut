import subprocess
import json

def get_video_duration(input_path):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', input_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])

def shorten_video(input_path, output_path, target_duration=59):
    # Get the original duration
    original_duration = get_video_duration(input_path)
    
    # Calculate the speed factor
    speed_factor = original_duration / target_duration
    
    # Construct the FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-filter_complex', f'[0:v]setpts={1/speed_factor}*PTS[v];[0:a]atempo={speed_factor}[a]',
        '-map', '[v]',
        '-map', '[a]',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-y',  # Overwrite output file if it exists
        output_path
    ]
    
    # Run the FFmpeg command
    subprocess.run(cmd, check=True)

# Example usage
input_video = "data/final/lm2-test-final_segment_6.mp4"
output_video = "data/final/output_video_4.mp4"
shorten_video(input_video, output_video)