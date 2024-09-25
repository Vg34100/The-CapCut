import datetime
import whisper
import whisper.utils

def time_to_srt_format(seconds):
    time = datetime.timedelta(seconds=seconds)
    hours, remainder = divmod(time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = time.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def create_subtitle(index, start, end, text):
    return f"{index}\n{start} --> {end}\n{text}\n\n"

def convert_result_to_srt(result):
    segments = result['segments']
    
    srt_content = ""
    for index, segment in enumerate(segments, 1):
        start = time_to_srt_format(segment['start'])
        end = time_to_srt_format(segment['end'])
        text = segment['text'].strip()
        
        srt_content += create_subtitle(index, start, end, text)
    
    return srt_content

# Load the model and transcribe the audio
model = whisper.load_model("medium.en")
result = model.transcribe(r"data\out\audio.mp3")

# Convert the result to SRT format
srt_output = convert_result_to_srt(result)

# Save the SRT output to a file
with open("data/out/subtitles.srt", "w", encoding="utf-8") as srt_file:
    srt_file.write(srt_output)

print("SRT file has been generated as 'subtitles.srt'")

# Print the full text of the video
print(f'The text in video:\n{result["text"]}')