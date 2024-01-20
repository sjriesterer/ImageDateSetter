import os
import re
from datetime import datetime
from PIL import Image, ExifTags
import piexif

# Searches a folder and subfolders for files
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
DEBUG = False
FOLDER_PATH = r'E:\Pictures\Photos\Test'

# -------------------------------------------------------------------
# METHODS
# -------------------------------------------------------------------
def extract_date_from_filename(filename):
    global DEBUG
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
    global DEBUG
    try:
        exif_dict = piexif.load(filename)
        # new_date = datetime(2018, 1, 1, 0, 0, 0).strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filename)
        if DEBUG:
            print("Date set")
    except (AttributeError, KeyError, IndexError, IOError) as e:
        if DEBUG:
            print(f"Error setting date taken for {filename}: {e}")
# -------------------------------------------------------------------

def is_datetime_original_set(image_path):
    global DEBUG
    try:
        img = Image.open(image_path)

        # Get the EXIF data
        exif_dict = piexif.load(img.info['exif'])

        # Check if DateTimeOriginal tag is present
        if piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
            if DEBUG:
                print("DateTimeOriginal is set:", exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal])
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
    global DEBUG
    for filename in os.listdir(folder_path):
        if DEBUG:
            print("\n---------\nProcessing : ", filename)
        file_path = os.path.join(folder_path, filename)
        if DEBUG:
            print("file path : ", file_path)
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
