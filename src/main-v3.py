# main.py
import logging
import os
import datetime
import re

from utils.cache_manager import move_to_cache, clean_cache
from utils.file_utils import generate_temp_filename, generate_cache_filename
from utils.video_utils import merge_audio_tracks, split_video, extract_audio, parse_segments, convert_to_9_16, add_subtitles
from utils.whisper_utils import generate_subtitles
from utils.decision_maker import decide_clips
from utils.log_manager import log_info, log_attribute, log_warning, log_error

CACHE_DIR = "data/cache"
TEMP_DIR = "data/temp"

def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

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
    log_info("Step 0: merging audio tracks...")
    if not os.path.exists(c_temp_video):
        temp_video = merge_audio_tracks(input_video, temp_video)
        if temp_video != input_video:
            move_to_cache(temp_video)
    else:
        log_info(f"Using cached merged video: {temp_video}")   
        temp_video = c_temp_video 
    
    # Step 1: Extract audio
    log_info("Step 1: extracting audio...")
    if not os.path.exists(c_audio_file):
        extract_audio(temp_video, audio_file)
        move_to_cache(audio_file)
    else:
        log_info(f"Using cached audio file: {audio_file}")
        audio_file = c_audio_file

    
    # Step 2: Generate subtitles
    log_info("Step 2: generating subtitles...")
    if not os.path.exists(c_srt_file):
        generate_subtitles(audio_file, TEMP_DIR)
        move_to_cache(srt_file)
    else:
        log_info(f"Using cached subtitles file: {srt_file}")
        srt_file = c_srt_file

    # Step 3: Decide on clip segments
    log_info("Step 3: deciding on clip segments...")
    if not os.path.exists(c_decision_file):
        decide_clips(srt_file, decision_file)
        move_to_cache(decision_file)
    else:
        log_info(f"Using cached decision file: {decision_file}")
        decision_file = c_decision_file

    # Step 4: Split video into segments
    log_info("Step 4: splitting video into segments...")
    timeframes = parse_segments(decision_file)
    split_video(temp_video, output_dir, timeframes)

    # Extract the base name from the input video file
    input_base_name = os.path.splitext(os.path.basename(input_video))[0]

    # Step 5: Convert each segment to 9:16 format and add subtitles
    segments = [seg for seg in os.listdir(output_dir) if seg.endswith('.mp4')]
    segments.sort(key=natural_sort_key)
    
    for i, segment in enumerate(segments, start=1):
        input_segment = os.path.join(output_dir, segment)
        temp_9_16 = os.path.join(output_dir, f"9_16_{segment}")
        final_output = os.path.join(final_output_dir, f"{input_base_name}_final_segment_{i:02d}.mp4")

        log_attribute(f"Converting segment {i} to 9:16 format...")
        convert_to_9_16(input_segment, temp_9_16)

        log_attribute(f"Re-generating subtitles for segment {i}...")
        temp_audio = os.path.join("data/temp", f"audio_{i:02d}.mp3")
        temp_srt = os.path.join("data/temp/", f"audio_{i:02d}.srt")
        extract_audio(temp_9_16, temp_audio)
        generate_subtitles(temp_audio, TEMP_DIR, True)

        log_attribute(f"Adding subtitles to segment {i}...")
        add_subtitles(temp_9_16, temp_srt, final_output)

        # Clean up temporary files
        os.remove(temp_9_16)
        os.remove(temp_audio)
        os.remove(temp_srt)
        os.remove(input_segment)

    # Move files to cache instead of deleting
    if temp_video != c_temp_video and temp_video != input_video: os.remove(temp_video)
    if audio_file != c_audio_file: os.remove(audio_file)
    if srt_file != c_srt_file: os.remove(srt_file)
    if decision_file != c_decision_file: os.remove(decision_file)
    
    # Clean up old files from the cache if needed
    clean_cache()

    log_info("All processing complete!")

if __name__ == "__main__":
    # input_video = r"A:\Projects\The Video Center\data\outputs\RAW__09-29-24__[09]\[VGL]-[ZEOW]-RAW__09-29-24__[09]-1.mp4"
    # #input_video = r"data/input/test2.mp4"
    # main(input_video)
    
    for input in [
        r"A:\Projects\The Video Center\data\outputs\RAW__09-29-24__[09]\[VGL]-[EOW]-RAW__09-29-24__[09]-1.mp4", 
        r"A:\Projects\The Video Center\data\outputs\RAW__09-29-24__[09]\[VGL]-[EOW]-RAW__09-29-24__[09]-2.mp4", 
        r"A:\Projects\The Video Center\data\outputs\RAW__09-29-24__[09]\[VGL]-[EOW]-RAW__09-29-24__[09]-3.mp4",
        r"A:\Projects\The Video Center\data\outputs\RAW__09-30-24__[20]\[VGL]-[EPM]-RAW__09-30-24__[20]-1.mp4",
        r"A:\Projects\The Video Center\data\outputs\RAW__09-30-24__[20]\[VGL]-[EPM]-RAW__09-30-24__[20]-2.mp4",
        ]:
        main(input)