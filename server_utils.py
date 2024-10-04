import requests
server_url='https://22ec-3-111-197-27.ngrok-free.app'
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

import os

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

def generate_prompt(prompt, url='/generate_prompt'):
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
    
def generate_text(prompt, url='/generate_text'):
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
    
def get_text_LLM_answer(user_input):
    ans=generate_text(prompt=user_input)
    title,subtitle, hashtags = extract_title_and_tags(ans)
    return title,subtitle, hashtags 


