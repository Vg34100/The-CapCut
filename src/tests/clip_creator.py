# clip_creator.py
import subprocess
import os

def time_to_seconds(time_str):
    """Convert time string to seconds."""
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h = '0'
        m, s = parts
    else:
        raise ValueError(f"Invalid time format: {time_str}")
    return int(h) * 3600 + int(m) * 60 + float(s)

def split_video(input_file, output_dir, timeframes):
    """Split video into segments based on given timeframes."""
    os.makedirs(output_dir, exist_ok=True)
    
    for i, (start, end) in enumerate(timeframes):
        output_file = os.path.join(output_dir, f"segment_{i+1}.mp4")
        duration = time_to_seconds(end) - time_to_seconds(start)
        
        cmd = [
            'ffmpeg',
            '-ss', start,
            '-i', input_file,
            '-t', str(duration),
            '-c', 'copy',  # Use copy mode for speed
            '-avoid_negative_ts', '1',
            output_file
        ]
        
        subprocess.run(cmd, check=True)
        print(f"Created segment {i+1}: {output_file}")

def parse_timeframes(timeframe_file):
    """Parse timeframe file into list of (start, end) tuples."""
    with open(timeframe_file, 'r') as file:
        lines = file.readlines()
    
    timeframes = []
    for line in lines:
        line = line.strip()
        if line:  # Skip empty lines
            start, end = line.strip('[]').split(' --> ')
            timeframes.append((start, end))
    return timeframes

# Example usage
input_file = "data/input/test1.mp4"
output_dir = "data/out"
timeframe_file = "data/temp/decision.txt"

timeframes = parse_timeframes(timeframe_file)
split_video(input_file, output_dir, timeframes)