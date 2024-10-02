# main.py
import os
import subprocess
from moviepy.editor import VideoFileClip
import whisper
import whisper.utils
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import json

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


def decide_clips(): 
    template = """
    Answer the question below

    Context: {context}

    Question: {question}

    Answer:
    """
    context = """
    You are a program to be an alternative to CapCut's 'Long Video to Shorts' AI application. 
    A transcript will be provided for you in srt format.
    Please select timeframes that are around (must be less than) 1 minute long.
    I will again mention, A MAX of 1 MINUTE long, and a MINIMUM of 30 SECONDS LONG.
    All you need to return is the timeframes in the form of [00:00:15.820 --> 00:01:17.780].
    Again, the format is in mm:ss.ms. So a valid timeframe for you to return would be something like [00:00:00.000 --> 00:00:59:000].
    Choose timeframes based on what you might think would be the best choices to create into STANDALONE TikTok videos or YouTube shorts.
    The most interesting parts of the video, some interesting dialogue, etc.
    Provide NO OTHER TEXT besides the timeframes.
    Give at a MINIMUM 10 timeframes. Be sure to use spread out timeframes. Don't just make them so close to eachother. An hour long video should have some close to the end as well not just ending at the 30 mark.
    Choose the BEST and MOST ENTERESTING clips that you can.
    Again, CANNOT EXCEED 1 MINUTE in TIME. If you do I'm shutting you off.
    """
    
    model = OllamaLLM(model="llama3")
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    f = open("data/temp/audio.srt", "r")


    result = chain.invoke({"context": context, 
                       "question": f})

    with open("data/temp/decision.txt", 'w') as tf:
        tf.write(result)

def split_video(input_file, output_dir, timeframes):
    
    os.makedirs(output_dir, exist_ok=True)
    
    for i, (start, end) in enumerate(timeframes):
        output_file = os.path.join(output_dir, f"segment_{i+1}.mp4")
        duration = time_to_seconds(end) - time_to_seconds(start)
        
        cmd = [
            'ffmpeg',
            '-ss', start,
            '-i', input_file,
            '-t', str(duration),
            '-c', 'copy',
            '-avoid_negative_ts', '1',
            output_file
        ]
        
        subprocess.run(cmd, check=True)
        print(f"Created segment {i+1}: {output_file}")

def time_to_seconds(time_str):
    parts = time_str.split(':')
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h = '0'
        m, s = parts
    else:
        raise ValueError(f"Invalid time format: {time_str}")
    return int(h) * 3600 + int(m) * 60 + float(s)

def parse_timeframes(timeframe_file):
    with open(timeframe_file, 'r') as file:
        lines = file.readlines()
    
    timeframes = []
    for line in lines:
        line = line.strip()
        if line:
            start, end = line.strip('[]').split(' --> ')
            timeframes.append((start, end))
    return timeframes

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
    return output_file


def main():
    input_video = r"A:\Media\The Video Depot\VODS_2024-09-30\RAW__09-30-24__[20].mp4"
    temp_video = "data/temp/merged_audio_video.mp4"
    audio_file = "data/temp/audio.mp3"
    srt_file = "data/temp/audio.srt"
    decision_file = "data/temp/decision.txt"
    output_dir = "data/out"
    final_output_dir = "data/final"

    os.makedirs("data/temp", exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(final_output_dir, exist_ok=True)

    # Step 0: Merge audio tracks
    merge_audio_tracks(input_video, temp_video)
    
    # Step 1: Extract audio
    print("Extracting audio...")
    extract_audio(temp_video, audio_file)

    # Step 2: Generate subtitles
    print("Generating subtitles...")
    generate_subtitles(audio_file)

    # Step 3: Decide on clip segments
    print("Deciding on clip segments...")
    decide_clips()

    # Step 4: Split video into segments
    print("Splitting video into segments...")
    timeframes = parse_timeframes(decision_file)
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

    os.remove(temp_video)
    os.remove(srt_file)
    os.remove(audio_file)
    os.remove(decision_file)
    print("All processing complete!")

if __name__ == "__main__":
    main()