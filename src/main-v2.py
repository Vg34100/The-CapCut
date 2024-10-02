# main.py
import datetime
import os
import re
import subprocess
from moviepy.editor import VideoFileClip
import whisper
import whisper.utils
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import json
import logging
import shutil
import time

CACHE_DIR = "data/cache"
TEMP_DIR = "data/temp"
MAX_CACHE_SIZE_MB = 1000  # Maximum cache size in M
MAX_CACHE_AGE_DAYS = 14  # Maximum file age in days

def generate_temp_filename(input_video, description, ext):
    """Generate a custom cache filename based on the input video name."""
    base_name = os.path.splitext(os.path.basename(input_video))[0]
    return os.path.join(TEMP_DIR, f"{base_name}-{description}.{ext}")

def generate_cache_filename(input_video, description, ext):
    """Generate a custom cache filename based on the input video name."""
    base_name = os.path.splitext(os.path.basename(input_video))[0]
    return os.path.join(CACHE_DIR, f"{base_name}-{description}.{ext}")

def move_to_cache(file_path):
    """Move a file to the cache folder."""
    if os.path.exists(file_path):
        new_path = os.path.join(CACHE_DIR, os.path.basename(file_path))
        shutil.copy(file_path, new_path)
        logging.info(f"Moved {file_path} to cache as {new_path}")

def clean_cache():
    """Clean up cache folder based on file age and total size."""
    logging.info("Cleaning up cache folder...")
    cache_files = [os.path.join(CACHE_DIR, f) for f in os.listdir(CACHE_DIR) if os.path.isfile(os.path.join(CACHE_DIR, f))]
    
    total_size = sum(os.path.getsize(f) for f in cache_files) / (1024 * 1024)  # Convert to MB
    current_time = time.time()
    
    # Sort files by creation time (oldest first)
    cache_files.sort(key=lambda f: os.path.getctime(f))
    
    for file in cache_files:
        file_age_days = (current_time - os.path.getctime(file)) / (60 * 60 * 24)  # Convert seconds to days
        
        if total_size > MAX_CACHE_SIZE_MB or file_age_days > MAX_CACHE_AGE_DAYS:
            logging.info(f"Removing cache file: {file} (Age: {file_age_days:.2f} days, Size: {os.path.getsize(file) / (1024 * 1024):.2f} MB)")
            total_size -= os.path.getsize(file) / (1024 * 1024)  # Subtract file size in MB
            os.remove(file)

def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)
    video.close()

def generate_subtitles(audio_file, options = False):
    model = whisper.load_model("medium.en")
    result = model.transcribe(audio_file, verbose=True, language='en', word_timestamps=True, task="transcribe")
    word_options = {
        "highlight_words": True,
        "max_words_per_line": 4
    }
    srt_writer = whisper.utils.get_writer("srt", "data/temp")
    srt_writer(result, audio_file, word_options if options else None)
    


def decide_clips(srt_file, decision_file): 
    template = """
    Answer the question below.

    Here is the context: {context}

    Transcript:
    {transcript}

    Answer:
    """

    context = """
    You are a program designed to be an alternative to CapCut's 'Long Video to Shorts' AI application.

    A transcript will be provided for you in SRT format.

    Please select timeframes that are less than 1 minute long, with a minimum of 30 seconds.

    For each selected timeframe, provide a JSON object with the following structure:

    {
        "timestamp": "[start time] --> [end time]",
        "description": "Why you chose this segment",
        "content": "The exact words spoken in this segment",
        "virality": 90,  // An integer from 1 to 100 indicating how viral you think it could be
        "title": "A possible title for this short"
    }

    Again, the timestamp format is mm:ss.ms (e.g., [00:00.000]).

    Choose timeframes based on what you think would make the best TikTok videos or YouTube shorts, focusing on the most interesting parts or dialogue.

    Provide **NO OTHER TEXT** besides the JSON objects.
    HOWEVER give them to me as "plain text", do not do ```json ``` thing. 
    MAKE SURE, all objects are wrapped inside an [] array AND objects are separated by commas, AS WELL AS no trailing commas after the last object.    
    """

    model = OllamaLLM(model="gemma2:27b")
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    with open(srt_file, "r") as f:
        transcript = f.read()

    result = chain.invoke({
        "context": context,
        "transcript": transcript
    })

    with open(decision_file, 'w') as tf:
        tf.write(result)

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


def main(input_video):
    # Configure logging
    log_folder = "log"
    os.makedirs(log_folder, exist_ok=True)
    log_filename = os.path.join(log_folder, f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    # Ensure cache folder exists
    os.makedirs(CACHE_DIR, exist_ok=True)


    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_filename), logging.StreamHandler()]
    )    
    
    temp_video = generate_temp_filename(input_video, "merged", "mp4")
    audio_file = generate_temp_filename(input_video, "audio", "mp3")
    srt_file = generate_temp_filename(input_video, "audio", "srt")
    decision_file = generate_temp_filename(input_video, "decision", "json")
    
    c_temp_video = generate_cache_filename(input_video, "merged", "mp4")  # Cache merged video
    c_audio_file = generate_cache_filename(input_video, "audio", "mp3")  # Cache audio file
    c_srt_file = generate_cache_filename(input_video, "audio", "srt")  # Cache SRT file
    c_decision_file = generate_cache_filename(input_video, "decision", "json")  # Cache decision JSON
    

    output_dir = "data/out"
    final_output_dir = "data/final"

    os.makedirs("data/temp", exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(final_output_dir, exist_ok=True)

    # Step 0: Merge audio tracks
    print("Merging audio...")
    logging.info("Step 0: merging audio tracks...")
    if not os.path.exists(c_temp_video):
        temp_video = merge_audio_tracks(input_video, temp_video)
        move_to_cache(temp_video)
    else:
        logging.info(f"Using cached merged video: {temp_video}")    
    
    # Step 1: Extract audio
    print("Extracting audio...")
    logging.info("Step 1: extracting audio...")
    if not os.path.exists(c_audio_file):
        extract_audio(temp_video, audio_file)
        move_to_cache(audio_file)
    else:
        logging.info(f"Using cached audio file: {audio_file}")
    
    # Step 2: Generate subtitles
    print("Generating subtitles...")
    logging.info("Step 2: generating subtitles...")
    if not os.path.exists(c_srt_file):
        generate_subtitles(audio_file)
        move_to_cache(srt_file)
    else:
        logging.info(f"Using cached subtitles file: {srt_file}")

    # Step 3: Decide on clip segments
    print("Deciding on clip segments...")
    logging.info("Step 3: deciding on clip segments...")
    if not os.path.exists(c_decision_file):
        decide_clips(srt_file, decision_file)
        move_to_cache(decision_file)
    else:
        logging.info(f"Using cached decision file: {decision_file}")

    # Step 4: Split video into segments
    print("Splitting video into segments...")
    logging.info("Step 4: splitting video into segments...")
    timeframes = parse_segments(decision_file)
    split_video(temp_video, output_dir, timeframes)

    # Step 5: Convert each segment to 9:16 format and add subtitles
    for i, segment in enumerate(os.listdir(output_dir)):
        if segment.endswith('.mp4'):
            input_segment = os.path.join(output_dir, segment)
            temp_9_16 = os.path.join(output_dir, f"9_16_{segment}")
            final_output = os.path.join(final_output_dir, f"final_{segment}")

            print(f"Converting segment {i+1} to 9:16 format...")
            convert_to_9_16(input_segment, temp_9_16)

            print(f"Re-generating subtitles for segment {i+1}...")
            temp_audio = os.path.join("data/temp", f"audio_{i+1}.mp3")
            temp_srt = os.path.join("data/temp/", f"audio_{i+1}.srt")
            extract_audio(temp_9_16, temp_audio)
            generate_subtitles(temp_audio, True)

            print(f"Adding subtitles to segment {i+1}...")
            add_subtitles(temp_9_16, temp_srt, final_output)

            # Clean up temporary files
            os.remove(temp_9_16)
            os.remove(temp_audio)
            os.remove(temp_srt)
            os.remove(input_segment)

    # Move files to cache instead of deleting
    os.remove(temp_video)
    os.remove(audio_file)
    os.remove(srt_file)
    os.remove(decision_file)
    
    # Clean up old files from the cache if needed
    clean_cache()

    logging.info("All processing complete!")
    print("All processing complete!")

if __name__ == "__main__":
    input_video = r"data/input/test2.mp4"
    main(input_video)