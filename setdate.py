import os
import re
from datetime import datetime
from PIL import Image, ExifTags

def extract_date_from_filename(filename):
    # Extract date from the filename (assuming the date is in the format yyyy-mm-dd)
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None

def set_date_taken(image, date_taken):
    try:
        # Get the existing EXIF data
        exif_data = image._getexif()
        # print(exif_data)
        
        # Set the 'DateTimeOriginal' tag with the provided date
        date_time_tag = ExifTags.TAGS.get('DateTimeOriginal')
        print("date_time_tag = ", date_time_tag)

        if not date_time_tag:
            print("setting date and time")
            exif_data[date_time_tag] = date_taken

            # Save the modified EXIF data
            # image.save(image.filename, exif=image.info)
            image.save(image.filename, exif=image.info.get('exif'))
            print(f"Date taken set to {date_taken} for {image.filename}")

    except (AttributeError, KeyError, IndexError, IOError) as e:
        print(f"Error setting date taken for {image.filename}: {e}")

def process_files(folder_path):
    for filename in os.listdir(folder_path):
        print("filename = ", filename)
        file_path = os.path.join(folder_path, filename)
        print(file_path)
        if os.path.isfile(file_path):
            try:
                # Open the image
                image = Image.open(file_path)

                # Check if 'DateTimeOriginal' tag is missing or empty
                date_time_tag = ExifTags.TAGS.get('DateTimeOriginal')
                print("date_time_tag = ", date_time_tag)
                if not date_time_tag or (date_time_tag not in image.info) or not image.info[date_time_tag]:
                    print("image has no date taken set")
                    # Extract date from the filename
                    extracted_date = extract_date_from_filename(filename)
                    extracted_date = r'1990:01:01 12:00:00'

                    print("extracted date = ", extracted_date)
                    if extracted_date:
                        # Use the extracted date to set 'date taken' in the EXIF data
                        set_date_taken(image, extracted_date)

            except (AttributeError, KeyError, IndexError, IOError) as e:
                # Ignore errors and move to the next file
                print(f"Error processing {file_path}: {e}")

# Example usage
folder_path = r'E:\Pictures\Photos\Test'
image_path = r'E:\Pictures\Photos\Test\1990-01-01 Samuel & siblings.jpg'

process_files(folder_path)
