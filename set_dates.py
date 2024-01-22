import os
import re
from pathlib import Path
from datetime import datetime
from PIL import Image, ExifTags
import piexif
from tqdm import tqdm
import logging

# DATE_TIME_ORIGINAL SETTER (works for only .jpg and .tiff)
# SETS MISSING DATES BASED ON THE FILENAME

# Searches a folder and subfolders for files ending with an extension in EXTENSIONS
# Ignores directories in IGNORE_DIRS
# If file is missing the 'DateTimeOriginal' EXIF tag
#   - Extracts the date from the filename matching these conditions:
#       - IMG_yyyymmddFilename.jpg
#       - yyyyFilename
#       - yyyy-mmFilename
#       - yyyy-mFilename
#       - yyyy-mm-ddFilename
#       - yyyy-m-ddFilename
#       - yyyy-m-dFilename
#       - yyyymm
#       - yyymmddFilename
#   If missing month or day, sets them to 1
#   Time is set for midnight 12:00:00
#   Sets the 'DateTimeOriginal' EXIF tag to the extracted date

# -------------------------------------------------------------------
# GLOBALS
# -------------------------------------------------------------------
DEBUG = False # For debugging printouts
FOLDER_PATH = r'E:\Pictures\Photos' # Root folder to search
FOLDER_PATH = r"E:\Pictures\Photos\2023"
# FOLDER_PATH = r"E:\Photos"
EXTENSIONS = ['.jpg', '.tiff'] # Only files with these extensions will be processed
IGNORE_DIRS = [] # Will not process directories listed here
LOG_FILE = 'set_date_log.txt' # Output the logs to this file
APPEND = False # Appends log statements to file if true
PRINT_LOG = False # Prints the log statement to console if true
FORCE_DATE = False # Will set the DateTime tag based on the filename even if EXIF tag is already set
FORCE_EXIF_ERROR_TO_SET = True # Will force setting date even if error in checking if date is already set

# -------------------------------------------------------------------
# COUNTERS
# -------------------------------------------------------------------
images_set = 0
images_forced = 0
images_excluded = 0
images_invalid_image = 0
images_error_setting_exif = 0
images_error_extracting_exif = 0
images_previously_set = 0
images_forced_error_set = 0
images_invalid_filename = 0

num_files_to_process = 0

error_extracting_exif = False

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
def extract_date_from_filename(file_path):
    # Extracts the filename from a file path by splitting by '\'
    def extract_filename(file_path):
        parts = file_path.split('\\')

        # Return the last group
        if parts:
            return parts[-1]
        else:
            return None

    def match_pattern(pattern):
        filename = extract_filename(file_path)
        match = re.search(pattern, filename)
        if DEBUG:
            print(filename, " : ", pattern, " : ", match)
        return match.group(1) if match else None

    date_patterns = {
        'IMG_yyyymmddFilename.jpg': r'IMG_(\d{8})(.+)?\.jpg',
        'yyyy-mm-dd': r'(\d{4}-\d{1,2}-\d{1,2})',
        'yyyy-mm-dd filename': r'(\d{4}-\d{1,2}-\d{1,2})(?:\s(.+))?',
        'yyyy-mm filename.jpg': r'(\d{4}-\d{1,2})(?:\s(.+))?',
        'yyyy-mm.jpg': r'(\d{4}-\d{2})',
        'yyyymmdd filename.jpg': r'(\d{8})(?:\s(.+))?',
        'yyyymm filename.jpg': r'(\d{6})(?:\s(.+))?',
        'yyyy filename.jpg': r'(\d{4})(?:\s(.+))?',
    }

    for pattern_name, pattern in date_patterns.items():
        matched_date = match_pattern(pattern)
        if matched_date:
            if DEBUG:
                print("Found match date: ", matched_date)
            
            # Handle case where matched date is in the form of 6 digits (yyyymmdd)
            date_match = re.match(r'(\d{8})', matched_date)
            if date_match:
                matched_date = matched_date[:4] + '-' + matched_date[4:6] + '-' + matched_date[6:]
                if matched_date[-2:] == "00": # Some dates are in the form of yyyymm00
                    matched_date = matched_date[:-2] + "01"
            else:
                # Handle case where matched date is in the form of 6 digits (yyyymm)
                date_match = re.match(r'(\d{4})(\d{2})', matched_date)
                if date_match:
                    matched_date = matched_date[:4] + "-" + matched_date[4:]

                if matched_date.count('-') == 0:
                    matched_date += '-01-01'  # Set month and day to 01 for patterns with only the year
                elif matched_date.count('-') == 1:
                    matched_date += '-01'  # Set day to 01 for patterns with only year-month

            try:
                new_date = datetime.strptime(matched_date, "%Y-%m-%d").strftime("%Y:%m:%d %H:%M:%S")
                return new_date
            except ValueError:
                if DEBUG:
                    print("Unable to extract date from filename")
                return None

    return None
# -------------------------------------------------------------------

def set_date_taken(filename, new_date, previous_date):
    global images_set
    global images_forced
    global images_excluded
    global images_invalid_image
    global images_error_setting_exif

    try:
        exif_dict = piexif.load(filename)
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filename)
        if previous_date is None:
            images_set = images_set + 1
            logging.info(f"Date Set ` {filename} ` {new_date} ` ` ")
        else:
            images_forced = images_forced + 1
            logging.info(f"Forced Date Set ` {filename} ` {new_date} ` {previous_date} ` ")
    except piexif.InvalidImageDataError:
        images_invalid_image = images_invalid_image + 1
        logging.info(f"Not Image File ` {filename} ` {new_date} ` ` (Invalid Image Data)")
    except Exception as e:
        # Capture any other exceptions and log the error
        images_error_setting_exif = images_error_setting_exif + 1
        logging.info(f"Error ` {filename} ` {new_date} ` ` {e}")
# -------------------------------------------------------------------

def is_datetime_original_set(image_path):
    global images_previously_set
    global images_error_extracting_exif
    global error_extracting_exif
    
    try:
        img = Image.open(image_path)

        # Get the EXIF data
        exif_dict = piexif.load(img.info['exif'])

        # Check if DateTimeOriginal tag is present
        if piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
            previous_date = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]
            if not FORCE_DATE:
                images_previously_set = images_previously_set + 1
                logging.info(f"Set Previously ` {image_path} ` {previous_date} ` ` ")

            return previous_date
        else:
            if DEBUG:
                print("DateTimeOriginal is not set.")
            return None

    except Exception as e:
        error_extracting_exif = True
        return None
# -------------------------------------------------------------------

def process_files(folder_path):
    global images_excluded
    global images_error_extracting_exif
    global error_extracting_exif
    global images_forced_error_set
    global num_files_to_process
    global images_invalid_filename

    all_files = []

    # Build a list of all files in directory and sub directories
    for root, dirs, files in os.walk(folder_path):
        # Check if any of the directories in IGNORE_DIRS are present in the current path
        if any(ignore_dir in root for ignore_dir in IGNORE_DIRS):
            continue

        all_files.extend(os.path.join(root, filename) for filename in files)

    num_files_to_process = len(all_files)

    if DEBUG:
        print("Found ", num_files_to_process, " files")

    # Iterate through each file
    for file_path in tqdm(all_files, desc="Processing Image Files", unit="file", leave=False):
        if DEBUG:
            print("\n---------\nProcessing : ", file_path)

        file_path = os.path.join(root, file_path)

        if DEBUG:
            print("file path : ", file_path)

        # Check if the file has an allowed extension
        if Path(file_path).suffix.lower() not in EXTENSIONS:
            images_excluded = images_excluded + 1
            logging.info(f"Excluded File ` {file_path} ` ` ` ")
            continue

        date_set = is_datetime_original_set(file_path)
        
        # Error in getting EXIF tag, skip image
        if date_set is None and error_extracting_exif and not FORCE_EXIF_ERROR_TO_SET:
            error_extracting_exif = False
            images_error_extracting_exif = images_error_extracting_exif + 1
            logging.info(f"Error Extracting EXIF Tag ` {file_path} ` ` ` exif ")

        # Date already set, skip image
        elif date_set and not FORCE_DATE:
            pass

        # Need to set date
        else:
            if DEBUG:
                print("Extracting date from filename")
            new_date = extract_date_from_filename(file_path)
            if new_date:
                if DEBUG:
                    print("Date extracted : ", new_date)
                set_date_taken(file_path, new_date, date_set)
            else:
                if DEBUG:
                    print("Date not extracted")
                images_invalid_filename = images_invalid_filename + 1
                logging.info(f"Error Invalid Filename ` {file_path} ` ` ` ")

# -------------------------------------------------------------------
# SCRIPT
# -------------------------------------------------------------------
process_files(FOLDER_PATH)

if num_files_to_process > 0:
    print("\nDone processing images:\n---------------------------------")
    print("Images previously set: ", images_previously_set)
    print("Images set: ", images_set)
    print("Images forced set: ", images_forced)
    print("Images error forced set: ", images_forced_error_set)
    print("Files  excluded: ", images_excluded)
    print("Invalid filenames: ", images_invalid_filename)
    print("Invalid images: ", images_invalid_image)
    print("Error in extract tag: ", images_error_extracting_exif)
    print("Error in setting date: ", images_error_setting_exif)
    print("---------------------------------")
    total_files = images_set + images_forced + images_previously_set + images_excluded + images_invalid_image + images_error_extracting_exif + images_forced_error_set + images_invalid_filename + images_error_setting_exif
    print("Total files: ", total_files)
    print("\n")
else:
    print("No files found in directory : ", FOLDER_PATH)