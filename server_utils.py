import requests

import io

import json
server_url='https://0bcf-13-127-201-227.ngrok-free.app'

def inpaint_image(image_path, bounding_boxes, output_path='inpainted_image.png'):
    """
    Sends a request to the inpainting API endpoint and saves the inpainted image.

    Parameters:
    - image_path: str, path to the image file to be inpainted.
    - bounding_boxes: list of tuples, each tuple containing (x1, y1, x2, y2) coordinates.
    - output_path: str, path where the inpainted image will be saved (default is 'inpainted_image.png').

    Returns:
    - success: bool, True if the image was successfully inpainted and saved, False otherwise.
    - error: str or None, error message if the request fails.
    """
    url = server_url+'/inpaint'

    try:
        with open(image_path, 'rb') as image_file:
            files = {
                'image': image_file
            }
            data = {
                'bboxes': json.dumps(bounding_boxes)  # Convert bounding boxes to a JSON string
            }

            response = requests.post(url, files=files, data=data)

            if response.status_code == 200:
                # Save the inpainted image to the specified output path
                with open(output_path, 'wb') as out_file:
                    out_file.write(response.content)
                return True, None  # Indicate success and no error
            else:
                return False, response.json().get('error', 'Unknown error occurred.')
    except Exception as e:
        return False, str(e)
def sam_method(image_path, text_input):
    url = server_url+'/process_image'  # URL of the Flask endpoint
    # Prepare the files and data
    
    files = {'image': open(image_path, 'rb')}  # Open the image file in binary mode
    data = {'text_input': text_input}
    # Send a POST request to the endpoint
    response = requests.post(url, files=files, data=data)
    # Check the response
    response=response.json()
    title_bbox = None
    subtitle_bbox = None  # Placeholder for subtitle (not provided in the data)
    product_bbox=None
    for item in response['results']:
        try:
            label = item['result']['bboxes_labels'][0]
            bbox = item['result']['bboxes'][0]

            if label == text_input.split(',')[0]:
                title_bbox = bbox
            elif label == text_input.split(',')[1]:  # Assuming hashtags could serve as a subtitle
                subtitle_bbox = bbox
            elif label == text_input.split(',')[2]:  # Assuming hashtags could serve as a subtitle
                product_bbox = bbox
        except:
            pass
    return title_bbox,subtitle_bbox,product_bbox


from PIL import Image
from io import BytesIO
import requests
# Define the URL of the Flask endpoint
def image_generation(img_path,prompt):
    url = server_url+'/generate'
    # Path to the image you want to upload
    # Define your text prompt

    # Open the image file in binary mode
    with open(img_path, 'rb') as image_file:
        # Prepare the files and data for the request
        files = {'image': image_file}
        data = {'prompt': prompt}
        # Send the POST request
        response = requests.post(url, files=files, data=data)
    # Check the response
    if response.status_code == 200:
        # Save the generated image
        image=Image.open(BytesIO(response.content))
        print("Image generated and saved as output_image.png")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        
    return image


import re


def extract_title_and_tags(text):
    # Regular expression patterns
    title_pattern = r"\*\*Title\*\*: (.*?)(?:\n|$)"
    subtitle_pattern = r"\*\*Subheading\*\*: (.*?)(?:\n|$)"  # Fixing the typo "Suheading"
    tags_pattern = r"#\w+"

    # Extract title
    title_match = re.search(title_pattern, text, re.DOTALL)
    title = title_match.group(1).strip() if title_match else "No title found"

    # Extract subtitle
    subtitle_match = re.search(subtitle_pattern, text, re.DOTALL)
    subtitle = subtitle_match.group(1).strip() if subtitle_match else "No subtitle found"

    # Extract hashtags
    hashtags = re.findall(tags_pattern, text)
    hashtags_str = ', '.join(hashtags) if hashtags else "No hashtags found"

    # Return results as separate strings
    return title, subtitle, hashtags_str


import requests

def generate_prompt(prompt, url='/generate-prompt'):
    url=server_url+url
    """
    Sends a prompt to the Flask server and returns the generated text.
    Parameters:
    - prompt (str): The text prompt to send to the server.
    - url (str): The endpoint URL of the Flask server.
    Returns:
    - str: The generated text response from the server.
    """
    # Create the payload
    payload = {'prompt': prompt}
    try:
        # Send the POST request to the Flask endpoint
        response = requests.post(url, json=payload)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            return response.json().get('generated_text', {}).get('response', 'No response found.')
        else:
            return f"Error: {response.json().get('error', 'Unknown error')}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def generate_text(prompt, url='/generate-title'):
    url=server_url+url
    """
    Sends a prompt to the Flask server and returns the generated text.
    Parameters:
    - prompt (str): The text prompt to send to the server.
    - url (str): The endpoint URL of the Flask server.
    Returns:
    - str: The generated text response from the server.
    """
    # Create the payload
    payload = {'prompt': prompt}
    try:
        # Send the POST request to the Flask endpoint
        response = requests.post(url, json=payload)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            return response.json().get('title', {})
        else:
            return f"Error: {response.json().get('error', 'Unknown error')}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def get_text_LLM_answer(user_input):
    ans=generate_text(prompt=user_input)
    title,subtitle, hashtags = extract_title_and_tags(ans)
    return title,subtitle, hashtags 

import base64

def pil_image_to_bytes(image: Image) -> str:
    img_io = io.BytesIO()
    image.save(img_io, format='PNG')  # Save as PNG or any other format you prefer
    img_io.seek(0)
    return base64.b64encode(img_io.read()).decode('utf-8')

# Paste Image
def paste_image(base_image: Image, paste_image: Image, bbox):
    url = f'{server_url}/paste_image'
    data = {
        'base_image': pil_image_to_bytes(base_image),
        'paste_image': pil_image_to_bytes(paste_image),
        'bbox': bbox
    }
    response = requests.post(url, json=data)
    return Image.open(io.BytesIO(response.content))

# Inpaint Image
def inpaint_image(image: Image, bounding_boxes, inpaint_radius=3):
    url = f'{server_url}/inpaint'
    data = {
        'image': pil_image_to_bytes(image),
        'bounding_boxes': bounding_boxes,
        'inpaint_radius': inpaint_radius
    }
    response = requests.post(url, json=data)
    return Image.open(io.BytesIO(response.content))

# Remove Text from Image
def remove_text(image: str):
    url = f'{server_url}/remove_text'
    data = {
        'image': pil_image_to_bytes(image)
    }
    response = requests.post(url, json=data)
    return Image.open(io.BytesIO(response.content))

def draw_text(image: Image, text: str, bbox: tuple, font_path: str = "arial.ttf", gradient_start=(100, 0, 0), gradient_end=(0, 0, 100)):
    url = f'{server_url}/draw_text'
    data = {
        'image': pil_image_to_bytes(image),
        'text': text,
        'bbox': bbox,
        'font_path': font_path,
        'gradient_start': gradient_start,
        'gradient_end': gradient_end
    }
    response = requests.post(url, json=data)
    return Image.open(io.BytesIO(response.content))
def get_text_LLM_answer(user_input):
    ans=generate_text(prompt=user_input)
    title,subtitle, hashtags = extract_title_and_tags(ans)
    return title,subtitle, hashtags