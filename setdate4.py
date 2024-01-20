import os
import re
from datetime import datetime
from PIL import Image, ExifTags
import piexif

def extract_date_from_filename(filename):
    new_date = datetime(2018, 1, 1, 0, 0, 0).strftime("%Y:%m:%d %H:%M:%S")
    return new_date

def set_date_taken(filename, new_date):
    try:
        exif_dict = piexif.load(filename)
        # new_date = datetime(2018, 1, 1, 0, 0, 0).strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filename)

    except (AttributeError, KeyError, IndexError, IOError) as e:
        print(f"Error setting date taken for {filename}: {e}")

def is_datetime_original_set(image_path):
    try:
        # Open the image using the Pillow library
        img = Image.open(image_path)

        # Get the EXIF data
        exif_dict = piexif.load(img.info['exif'])

        # Check if DateTimeOriginal tag is present
        if piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
            print("DateTimeOriginal is set:", exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal])
            return True
        else:
            print("DateTimeOriginal is not set.")
            return False

    except Exception as e:
        print("Error:", e)
        return False
    
def process_files(folder_path):
    for filename in os.listdir(folder_path):
        print("filename = ", filename)
        file_path = os.path.join(folder_path, filename)
        print(file_path)
        if os.path.isfile(file_path):
            date_set = is_datetime_original_set(file_path)
            if not date_set:
                new_date = extract_date_from_filename(file_path)
                set_date_taken(file_path, new_date)

# Example usage
folder_path = r'E:\Pictures\Photos\Test'
image_path = r'E:\Pictures\Photos\Test\1990-01-01 Samuel & siblings.jpg'

process_files(folder_path)
