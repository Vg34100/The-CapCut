import whisper

def generate_subtitles(audio_file, temp_dir, options = False):
    model = whisper.load_model("medium.en")
    result = model.transcribe(audio_file, verbose=True, language='en', word_timestamps=True, task="transcribe")
    word_options = {
        "highlight_words": True,
        "max_words_per_line": 4
    }
    srt_writer = whisper.utils.get_writer("srt", temp_dir)
    srt_writer(result, audio_file, word_options if options else None)
    