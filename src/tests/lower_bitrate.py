import sys
import subprocess

def process_audio(input_file, output_file, target_bitrate=128):
    """
    Convert multi-channel audio to stereo and lower the bitrate using FFmpeg.
    
    :param input_file: Path to the input audio file
    :param output_file: Path to save the output audio file
    :param target_bitrate: Target bitrate in kbps (default: 128)
    """
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', input_file,
        '-ac', '2',             # Convert to 2 channels (stereo)
        '-c:a', 'aac',          # Use AAC encoder
        '-b:a', f'{target_bitrate}k',
        '-movflags', '+faststart',  # Optimize for web streaming
        '-af', 'aresample=resampler=soxr',  # High-quality resampling
        output_file
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Successfully converted {input_file} to stereo and processed to target bitrate {target_bitrate}kbps")
        print(f"Output saved as {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr.decode()}")
    except FileNotFoundError:
        print("FFmpeg not found. Please ensure FFmpeg is installed and added to your system PATH.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py input_file output_file [target_bitrate]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    target_bitrate = int(sys.argv[3]) if len(sys.argv) > 3 else 128
    
    process_audio(input_file, output_file, target_bitrate)