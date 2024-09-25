from moviepy.editor import VideoFileClip

def extract_audio(video_path, audio_path):
    # Load the video file
    video = VideoFileClip(video_path)
    
    # Extract the audio
    audio = video.audio
    
    # Write the audio to a file
    audio.write_audiofile(audio_path)
    
    # Close the video file
    video.close()

# Example usage
video_file = "data/input/test1.mp4"
audio_file = "data/out/audio.mp3"

extract_audio(video_file, audio_file)
print(f"Audio extracted to {audio_file}")