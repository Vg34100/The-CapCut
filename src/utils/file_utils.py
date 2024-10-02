import os

TEMP_DIR = "data/temp"
CACHE_DIR = "data/cache"

def generate_temp_filename(input_video, description, ext):
    """Generate a temporary filename based on the input video."""
    base_name = os.path.splitext(os.path.basename(input_video))[0]
    return os.path.join(TEMP_DIR, f"{base_name}-{description}.{ext}")

def generate_cache_filename(input_video, description, ext):
    """Generate a cache filename based on the input video."""
    base_name = os.path.splitext(os.path.basename(input_video))[0]
    return os.path.join(CACHE_DIR, f"{base_name}-{description}.{ext}")
