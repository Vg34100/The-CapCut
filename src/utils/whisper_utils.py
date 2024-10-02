import whisper

def generate_subtitles(audio_file, output_srt_file):
    """Generate subtitles using Whisper."""
    model = whisper.load_model("medium.en")
    result = model.transcribe(audio_file, language='en', word_timestamps=True)
    with open(output_srt_file, 'w') as f:
        f.write(result['text'])
