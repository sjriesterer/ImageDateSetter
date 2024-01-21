import os
import re
from pathlib import Path
from datetime import datetime
from PIL import Image, ExifTags
import piexif
import logging

# Searches a folder and subfolders for files ending with an extension in EXTENSIONS
# Ignores directories in IGNORE_DIRS
# Checks if 'DateTimeOriginal EXIF tag is set for file

# -------------------------------------------------------------------
# GLOBALS
# -------------------------------------------------------------------
DEBUG = True # For debugging printouts
FOLDER_PATH = r'E:\Pictures\Photos\2000' # Root folder to search
EXTENSIONS = ['.jpg', '.png'] # Only files with these extensions will be processed
IGNORE_DIRS = ['2000-00 Various'] # Will not process directories listed here
LOG_FILE = 'missing_dates_log.txt' # Output to logs to this file
APPEND = False # Appends log statements to file if true
PRINT_LOG = False # Prints the log statement to console if true

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

if PRINT_LOG:
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
            logging.info(f"Set Previously ` {image_path} ` {exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]} ` ")
            return True
        else:
            logging.info(f"Not Set ` {image_path} ` ` ")
            return False

    except Exception as e:
        logging.info(f"Error ` {image_path} ` ` {e}")
        return False
# -------------------------------------------------------------------

def process_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        # Check if any of the directories in IGNORE_DIRS are present in the current path
        if any(ignore_dir in root for ignore_dir in IGNORE_DIRS):
            continue
       
        for filename in files:
            if DEBUG:
                print("\n---------\nProcessing : ", filename)

            file_path = os.path.join(root, filename)

            if DEBUG:
                print("file path : ", file_path)

            # Check if the file has an allowed extension
            if os.path.isfile(file_path) and Path(file_path).suffix.lower() not in EXTENSIONS:
                logging.info(f"Invalid File ` {file_path} ` ` ")
                continue
            else:
                date_set = is_datetime_original_set(file_path)

# -------------------------------------------------------------------
# SCRIPT
# -------------------------------------------------------------------
process_files(FOLDER_PATH)
