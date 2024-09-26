import subprocess
import json

def count_audio_streams(input_file):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', input_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse the JSON output
    data = json.loads(result.stdout)
    
    # Count audio streams
    audio_streams = [stream for stream in data['streams'] if stream['codec_type'] == 'audio']
    return len(audio_streams)

def merge_audio_tracks(input_file, output_file):
    # Count audio streams
    num_audio_streams = count_audio_streams(input_file)
    print(f"Number of audio streams: {num_audio_streams}")

    if num_audio_streams <= 1:
        print("Video has 0 or 1 audio stream. No merging needed.")
        return

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

# Example usage
input_video = "data/input/RAW__09-24-24__[21].mp4"
output_video = "data/out/merged_audio_output.mp4"

merge_audio_tracks(input_video, output_video)