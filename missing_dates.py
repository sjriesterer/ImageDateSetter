import os
import re
from pathlib import Path
from datetime import datetime
from PIL import Image, ExifTags
import piexif
import logging

# Searches a folder and subfolders for files ending with an extension in EXTENSIONS
# If file is missing the 'DateTimeOriginal' EXIF tag
#   - Extracts the date from the filename matching these conditions:
#       - yyyyFilename
#       - yyyy-mmFilename
#       - yyyy-mFilename
#       - yyyy-mm-ddFilename
#       - yyyy-m-ddFilename
#       - yyyy-m-dFilename
#   If missing month or day, sets them to 1
#   Time is set for midnight 12:00:00
#   Sets the 'DateTimeOriginal' EXIF tag to the extracted date

# -------------------------------------------------------------------
# GLOBALS
# -------------------------------------------------------------------
DEBUG = True # For debugging printouts
FOLDER_PATH = r'E:\Pictures\Photos\1990' # Root folder to search
FOLDER_PATH = r'E:\Photos\1990' # Root folder to search
EXTENSIONS = ['.jpg', '.png', '.heic'] # Only files with these extensions will be processed
LOG_FILE = 'missing_dates_log.txt' # Output to logs to this file
APPEND = False # Appends log statements to file if true

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
# Delete the log file if APPEND is False
if not APPEND and os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

# Configure logging to write to both file and console
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s ` %(levelname)s ` %(message)s'
)

# Create a StreamHandler to print log messages to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Set the desired logging level for the console
console_formatter = logging.Formatter('%(asctime)s ` %(levelname)s ` %(message)s')
console_handler.setFormatter(console_formatter)

# Add the StreamHandler to the root logger
logging.getLogger().addHandler(console_handler)

# -------------------------------------------------------------------
# METHODS
# -------------------------------------------------------------------
def is_datetime_original_set(image_path):
    try:
        img = Image.open(image_path)

        # Get the EXIF data
        exif_dict = piexif.load(img.info['exif'])

        # Check if DateTimeOriginal tag is present
        if piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
            logging.info(f"Set Previously ` {image_path} ` {exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]}")
            return True
        else:
            logging.info(f"Not Set ` {image_path} ` ")
            return False

    except Exception as e:
        if DEBUG:
            print("Error:", e)
        return False
# -------------------------------------------------------------------

def process_files(folder_path):
    for filename in os.listdir(folder_path):
        if DEBUG:
            print("\n---------\nProcessing : ", filename)
        file_path = os.path.join(folder_path, filename)
        if DEBUG:
            print("file path : ", file_path)
        
        # Check if the file has an allowed extension
        if os.path.isfile(file_path) and Path(file_path).suffix.lower() not in EXTENSIONS:
            continue
        else:
            date_set = is_datetime_original_set(file_path)

# -------------------------------------------------------------------
# SCRIPT
# -------------------------------------------------------------------
process_files(FOLDER_PATH)
