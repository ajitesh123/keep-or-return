import streamlit as st
import threading
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

def make_dual_ai_calls(image: Image) -> Tuple[str, str]:
    stylist_prompt = f"""
    Act as a fashion stylist and rate this outfit based on fashion theory, material, texture etc.

    Output in markdown format.
    """
    
    mother_prompt = f"""Act as my mother and give your verdict on this outfit, considering emotions.

    Output in markdown format.
    """

    stylist_result = None
    mother_result = None

    def stylist_thread(image_copy):
        nonlocal stylist_result
        try:
            stylist_result = ask_openai_with_image_and_prompt(image_copy, stylist_prompt)
        except Exception as e:
            stylist_result = f"Error in stylist thread: {str(e)}"

    def mother_thread(image_copy):
        nonlocal mother_result
        try:
            mother_result = ask_openai_with_image_and_prompt(image_copy, mother_prompt)
        except Exception as e:
            mother_result = f"Error in mother thread: {str(e)}"

    image_copy = image.copy()  # Create a copy of the image to avoid thread safety issues

    t1 = threading.Thread(target=stylist_thread, args=(image_copy,))
    t2 = threading.Thread(target=mother_thread, args=(image_copy,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    return stylist_result, mother_result


# Create a Streamlit interface
def main():
    st.sidebar.title("Outfit Rating App")
    uploaded_image = st.sidebar.file_uploader("Upload an image of your outfit", type=["png", "jpg", "jpeg"])

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        stylist_result, mother_result = make_dual_ai_calls(image)
        st.markdown("# Fashion Stylist's Verdict")
        st.markdown(stylist_result)
        st.markdown("# Mother's Verdict")
        st.markdown(mother_result)

if __name__ == "__main__":
    main()
