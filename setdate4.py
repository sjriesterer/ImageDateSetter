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
DEBUG = False # For debugging printouts
FOLDER_PATH = r'E:\Pictures\Photos\Test' # Root folder to search
EXTENSIONS = ['.jpg', '.png', '.heic'] # Only files with these extensions will be processed
LOG_FILE = 'set_date_log.txt' # Output to logs to this file
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
def extract_date_from_filename(filename):
    def match_pattern(pattern):
        match = re.search(pattern, filename)
        return match.group(1) if match else None

    date_patterns = {
        'yyyy-mm-dd': r'(\d{4}-\d{1,2}-\d{1,2})',
        'yyyy-mm-dd filename': r'(\d{4}-\d{1,2}-\d{1,2})(?:\s(.+))?',
        'yyyy-mm filename.jpg': r'(\d{4}-\d{1,2})(?:\s(.+))?',
        'yyyy filename.jpg': r'(\d{4})(?:\s(.+))?',
    }

    for pattern_name, pattern in date_patterns.items():
        matched_date = match_pattern(pattern)
        if matched_date:
            if 'filename' in pattern_name and matched_date.count('-') < 2:
                matched_date += '-01'  # Set day to 01 for patterns with 'filename' and only year-month
            try:
                new_date = datetime.strptime(matched_date, "%Y-%m-%d").strftime("%Y:%m:%d %H:%M:%S")
                return new_date
            except ValueError:
                # Handle the case where only year and month are available
                new_date = datetime.strptime(matched_date, "%Y-%m").strftime("%Y:%m:%d %H:%M:%S")
                return new_date + '-01'

    return None
# -------------------------------------------------------------------

def set_date_taken(filename, new_date):
    try:
        exif_dict = piexif.load(filename)
        # new_date = datetime(2018, 1, 1, 0, 0, 0).strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filename)
        logging.info(f"Date set ` {filename} ` {new_date}")
        # print("Date set ' ", filename, " ` ", new_date)
    except (AttributeError, KeyError, IndexError, IOError) as e:
        logging.info(f"Error setting date ` {filename} ` {new_date} ` {e}")
# -------------------------------------------------------------------

def is_datetime_original_set(image_path):
    try:
        img = Image.open(image_path)

        # Get the EXIF data
        exif_dict = piexif.load(img.info['exif'])

        # Check if DateTimeOriginal tag is present
        if piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
            # print("Set Previously ` ", image_path, " ` ", exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal])
            logging.info(f"Set Previously ` {image_path} ` {exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]}")

            return True
        else:
            if DEBUG:
                print("DateTimeOriginal is not set.")
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
        if Path(file_path).suffix.lower() not in EXTENSIONS:
            continue

        if os.path.isfile(file_path):
            date_set = is_datetime_original_set(file_path)
            if not date_set:
                if DEBUG:
                    print("Extracting date from filename")
                new_date = extract_date_from_filename(file_path)
                if new_date:
                    if DEBUG:
                        print("Date extracted : ", new_date)
                    set_date_taken(file_path, new_date)
                else:
                    if DEBUG:
                        print("Date not extracted")

# -------------------------------------------------------------------
# SCRIPT
# -------------------------------------------------------------------
process_files(FOLDER_PATH)
