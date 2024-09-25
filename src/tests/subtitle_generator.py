import datetime
import whisper
import whisper.utils

# Load the model and transcribe the audio
model = whisper.load_model("base")
result = model.transcribe(r"data\input\test1.mp4", verbose=True, language='en', word_timestamps=True, task="transcribe")

# Set VTT Line and words width
word_options = {
    "highlight_words": True,
#     "max_line_count": 1,
#     "max_line_width": 24,
    "max_words_per_line": 4
}

srt_writer = whisper.utils.get_writer("srt", "data/out")
# Write the result to an SRT file
srt_writer(result, r"data\input\test1.mp4", word_options)


print("SRT file has been generated.")
