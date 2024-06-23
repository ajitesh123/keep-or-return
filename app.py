# Import the necessary libraries
import streamlit as st
import openai
import base64
from PIL import Image
import io
import requests
import os

# Consider using environment variables or a configuration file for API keys.
# WARNING: Do not hardcode API keys in your code, especially if sharing or using version control.
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
def ask_openai_with_image(image, role):
    # Encode the uploaded image to base64
    base64_image = encode_image_to_base64(image)

    # Create the payload with the base64 encoded image
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": ""
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}"
                    }
                ]
            }
        ],
        "max_tokens": 4095
    }

    if role == "fashion_stylist":
        payload["messages"][0]["content"][0]["text"] = "As a fashion stylist, analyze the uploaded image and provide a recommendation on whether to keep or return the item, considering factors such as color theory, texture, and overall style. Provide a justification for your recommendation."
    elif role == "mother":
        payload["messages"][0]["content"][0]["text"] = "As a mother, analyze the uploaded image and provide a recommendation on whether to keep or return the item, considering factors such as practicality, appropriateness, and overall value. Provide a justification for your recommendation."
    else:
        payload["messages"][0]["content"][0]["text"] = "I've uploaded an image and I'd like to know what it depicts and any interesting details you can provide."
    
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

# Create a Streamlit interface
st.title("GPT-4 with Vision")
st.write("Upload an image and get a description from GPT-4 with Vision.")

role = st.radio("Select a role", ("Fashion Stylist", "Mother"))

uploaded_image = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    if role == "Fashion Stylist":
        response = ask_openai_with_image(image, "fashion_stylist")
    else:
        response = ask_openai_with_image(image, "mother")
    st.write(response)