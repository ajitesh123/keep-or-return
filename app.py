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

def make_dual_ai_calls(image: Image, generate_caption: bool) -> Tuple[str, str, str]:
    stylist_prompt = f"""
    Act as a fashion stylist and rate this outfit based on fashion theory, material, texture etc.

    Output in markdown format.
    """
    
    mother_prompt = f"""Act as my mother and give your verdict on this outfit, considering emotions.

    Output in markdown format.
    """

    stylist_result = None
    mother_result = None
    instagram_caption = None

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
    
    def instagram_caption_thread(image_copy):
        nonlocal instagram_caption
        try:
            if generate_caption:
                instagram_caption = generate_instagram_caption(image_copy)
            else:
                instagram_caption = ""
        except Exception as e:
            instagram_caption = f"Error in Instagram caption generation: {str(e)}"

    image_copy = image.copy()  # Create a copy of the image to avoid thread safety issues

    t1 = threading.Thread(target=stylist_thread, args=(image_copy,))
    t2 = threading.Thread(target=mother_thread, args=(image_copy,))
    t3 = threading.Thread(target=instagram_caption_thread, args=(image_copy,))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    return stylist_result, mother_result, instagram_caption

def generate_instagram_caption(image: Image) -> str:
    caption_prompt = """
    Generate an Instagram-style caption and hashtags for this outfit image.
    The caption should be engaging and trendy, followed by relevant hashtags.

    """
    return ask_openai_with_image_and_prompt(image, caption_prompt)
    

# Create a Streamlit interface
def main():
    st.sidebar.title("Outfit Rating App")
    uploaded_image = st.sidebar.file_uploader("Upload an image of your outfit", type=["png", "jpg", "jpeg"])
    generate_caption = st.sidebar.checkbox("Generate Instagram Caption")

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.sidebar.image(image, caption="Uploaded Outfit Image", use_column_width=True, width=200)
        with st.spinner("Generating results..."):
            stylist_result, mother_result, instagram_caption = make_dual_ai_calls(image, generate_caption)
        st.markdown("# Fashion Stylist's Verdict")
        st.markdown(stylist_result)
        st.markdown("# Mother's Verdict")
        st.markdown(mother_result)
        if generate_caption:
            st.markdown("# Instagram Caption")
            if instagram_caption.startswith("Error"):
                st.error(instagram_caption)
            else:
                st.markdown(instagram_caption)

if __name__ == "__main__":
    main()
