# Import the necessary libraries
import streamlit as st
import asyncio
from typing import Tuple
import openai
import base64
from PIL import Image
import io
import requests
import os
import dotenv
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

openai.api_key = os.getenv('OPENAI_API_KEY')
if openai.api_key is None:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# Function to encode the image to base64
def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

# Function to send the image to the OpenAI API and get a response
def ask_openai_with_image_and_prompt(image: Image, prompt: str) -> str:
    # Encode the uploaded image to base64
    base64_image = encode_image_to_base64(image)
    
    # Create the payload with the base64 encoded image
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}]}],
        "max_tokens": 4095
    }
    
    # Send the request to the OpenAI API
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {openai.api_key}"},
        json=payload
    )
    
    # Check if the request was successful
    if response.status_code == 200:
        response_json = response.json()
        print("Response JSON:", response_json)  # Print the raw response JSON
        try:
            # Attempt to extract the content text
            return response_json["choices"][0]["message"]["content"]
        except Exception as e:
            # If there is an error in the JSON structure, print it
            print("Error in JSON structure:", e)
            print("Full JSON response:", response_json)
            return "Error processing the image response."
    else:
        # If an error occurred, return the error message
        return f"Error: {response.text}"

# Create a Gradio interface
def main():
    st.title("Outfit Rating App")
    uploaded_image = st.file_uploader("Upload an image of your outfit", type=["png", "jpg", "jpeg"])

# Launch the app
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        stylist_result, mother_result = asyncio.run(make_dual_ai_calls(image))
        st.write("Fashion Stylist's Verdict:", stylist_result)
        st.write("Mother's Verdict:", mother_result)

if __name__ == "__main__":
    main()
async def make_dual_ai_calls(image: Image) -> Tuple[str, str]:
    stylist_prompt = "Act as a fashion stylist and rate this outfit based on color theory, material, texture etc."
    mother_prompt = "Act as my mother and give your verdict on this outfit, considering emotions."

    stylist_task = asyncio.create_task(ask_openai_with_image_and_prompt(image, stylist_prompt))
    mother_task = asyncio.create_task(ask_openai_with_image_and_prompt(image, mother_prompt))

    stylist_result, mother_result = await asyncio.gather(stylist_task, mother_task)
    return stylist_result, mother_result

