import os
import sys

from dotenv import load_dotenv
from geocr import *
from pdf2image import convert_from_path
from PIL import Image as ImagePIL
import random

delete_original = True
load_dotenv()
ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
api_key = os.getenv("GOOGLE_VISION_API_KEY")

prescan_image_dpi = 450
#recurse_this_dir = "D:/Ready for OCR/Hansard Debates"


# set the directory you want to start from from commandline argument if present
if len(sys.argv) > 1:
    recurse_this_dir = sys.argv[1]


# build a list of directories to process
dirs_to_process = [dirname for dirname in os.listdir(recurse_this_dir) if
                   os.path.isdir(os.path.join(recurse_this_dir, dirname))]

# revrse the list so we process the last directory first
dirs_to_process.reverse()

for dir_to_process in dirs_to_process:

    image_dir = recurse_this_dir + "/" + dir_to_process
    print(f"Processing {image_dir}...")

    # Loop through each file in the directory
    filenames = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
    random.shuffle(filenames)
    #filenames.reverse()

    for filename in filenames:

        sleep_time = random.randint(1, 5)
        print(f"Sleeping for {sleep_time} seconds...")
        remove_tmp_jpg = False

        # check file with extension .txt of the same prefix doesn't exist

        image_path = os.path.join(image_dir, filename)

        file_name_without_extension, _ = os.path.splitext(image_path)

        if os.path.exists(file_name_without_extension + ".txt"):
            print(f"Matching conversion for {filename} already exists. Skipping...")
            continue

        images_to_ocr_filenames = []

        # Check if the file is pdf and convert
        if filename.endswith(".pdf"):
            print(f"Converting {filename} to image...")
            remove_tmp_jpg = True

            # Convert PDF to images
            images_to_ocr = convert_from_path(image_path , dpi=prescan_image_dpi)


            if( len(images_to_ocr) > 1):
                print('Splitting PDF into multiple images...')
                index = 1
                for img in images_to_ocr:
                    img.save(f"{file_name_without_extension}_{index}.jpg", 'JPEG')
                    index += 1

                images_to_ocr_filenames = [f"{file_name_without_extension}_{index}.jpg" for index in range(1, len(images_to_ocr)+1)]
                print( f"Split into {len(images_to_ocr_filenames)} images." )
            else:
                images_to_ocr[0].save(file_name_without_extension + '.jpg')
                images_to_ocr_filenames = [file_name_without_extension + '.jpg']

        else:
            images_to_ocr_filenames = [image_path]

        print(f"Processing {len(images_to_ocr_filenames)} pages of {filename}...")

        for image_to_ocr in images_to_ocr_filenames:

            save_filename = file_name_without_extension + ".txt"

            Image(image_to_ocr)

            result = requestOCR(ENDPOINT_URL, api_key, image_to_ocr)

            if result.status_code != 200 or result.json().get('error'):
                delete_original = False
                print("Error")
            else:
                result = result.json()
                for index in range(len(result)):
                    # output first 100 chars
                    print(result['responses'][0]['textAnnotations'][0]['description'][:100]+'...')

                text_result = result['responses'][0]['textAnnotations'][0]

                #  save is prefixed with .txt not .jpg
                with open(save_filename, 'a', encoding='utf-8') as file:
                    # output each \n as new line
                    for aline in text_result['description'].split('\n'):
                        file.write(aline+'\n')

                # remove the image if it was a pdf
                if remove_tmp_jpg:
                    os.remove(image_to_ocr)
                    print(f"Removed temp {image_to_ocr}")

        # remove the original file
        if delete_original:
            os.remove(image_path)
            print(f"Removed original {image_path}")
