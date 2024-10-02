# clip_creator.py
import subprocess
import os
import json
import re

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

def main():
    # Example usage
    input_file = "data/input/test2.mp4"
    output_dir = "data/out"
    segment_file = "data/temp/decision.json"

    segments = parse_segments(segment_file)
    split_video(input_file, output_dir, segments)


if __name__ == "__main__":
    main()