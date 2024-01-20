import os
import re
from datetime import datetime
import pyexiv2

def extract_date_from_filename(filename):
    # Extract date from the filename (assuming the date is in the format yyyy-mm-dd)
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None

def set_date_taken(image, date_taken):
    try:
        # Open the image using pyexiv2
        metadata = pyexiv2.Image(image)
        metadata.read()

        # Set the 'Exif.Image.DateTime' tag with the provided date
        metadata['Exif.Image.DateTime'] = date_taken

        # Save the modified EXIF data
        metadata.write()
        print(f"Date taken set to {date_taken} for {image}")

    except Exception as e:
        print(f"Error setting date taken for {image}: {e}")

def process_files(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if os.path.isfile(file_path):
            try:
                # Check if 'DateTimeOriginal' tag is missing or empty
                date_time_tag = 'Exif.Image.DateTime'
                image_date = pyexiv2.Image(file_path).read_a_date(date_time_tag)

                if not image_date:
                    # Extract date from the filename
                    extracted_date = extract_date_from_filename(filename)

                    if extracted_date:
                        # Use the extracted date to set 'date taken' in the EXIF data
                        set_date_taken(file_path, extracted_date)

            except Exception as e:
                # Ignore errors and move to the next file
                print(f"Error processing {file_path}: {e}")

# Example usage
folder_path = 'E:\Pictures\Photos\Test'
process_files(folder_path)
