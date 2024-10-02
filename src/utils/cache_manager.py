import os
import shutil
import logging
import time

CACHE_DIR = "data/cache"
MAX_CACHE_SIZE_MB = 1000
MAX_CACHE_AGE_DAYS = 14

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
