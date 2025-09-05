import base64
import json

import openai
from pdf2image import convert_from_path
from base64 import b64encode
import os
import requests
from PIL import Image
from io import BytesIO
from openai import OpenAI
from urllib.parse import urlparse

openai.api_key = "YOUR_API_KEY"

image_dir = "D:\ocrme\openaitest"

# Loop through each file in the directory
for filename in os.listdir(image_dir):

    # check file with extension .txt of the same prefix doesn't exist


    image_path = os.path.join(image_dir, filename)

    file_name_without_extension, _ = os.path.splitext(image_path)

    if os.path.exists(file_name_without_extension + ".txt"):
        print(f"Text file for {filename} already exists. Skipping...")
        continue

    # Check if the file is pdf and convert
    if filename.endswith(".pdf"):
        print(f"Converting {filename} to image...")

        # Convert PDF to images
        converted_image = convert_from_path(image_path , dpi=200)
        converted_image[0].save(file_name_without_extension + '.jpg')
        converted_image = file_name_without_extension + '.jpg'
    else:
        converted_image = image_path

    print(f"Processing {converted_image}...")

    # Encode image to base64
    #encoded_image = None
    #with open(converted_image, "rb") as image_file:
    #    encoded_image = base64.b64encode(image_file.read())


    # Open the image file and encode it as a base64 string
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    encoded_image = encode_image(converted_image)


    # Create an instance of the OpenAI class
    client = openai.OpenAI( api_key="YOUR_API_KEY")

    # Call the GPT-4 Vision API for OCR

    response = client.chat.completions.create(
        model='gpt-4o',
        #response_format={"type": "text"},
        messages=[
            {
                "role": "system",
                "content": "You are an OCR tool converts images files to text output."
            },
            {
                "role": "user", "content": [
                    {
                        "type": "text", "text": "Convert everything in this image to text. If it looks like newspaper articles or a book, please provide the text in a structured format."
                    },
                    {
                        "type": "image_url", "image_url":
                        {
                            "url": f"data:image/png;base64,{encoded_image}"
                        }
                    }
                ]
            },
        ],
        max_tokens=4000,
    )

    print(response.choices[0].message.content)

    # Get the OCR text from the response
    ocr_text = response.choices[0].message.content

    # Create a text file with the OCR text
    output_filename = file_name_without_extension + ".txt"

    with open(output_filename, "w", encoding="utf-8") as output_file:
        output_file.write(ocr_text)

    print(f"OCR text for {filename} saved to {output_filename}")
