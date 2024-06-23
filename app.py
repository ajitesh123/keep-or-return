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
def encode_image_to_base64(input_image):
    buffered = io.BytesIO()
    input_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

# Function to send the image to the OpenAI API and get a response
def ask_openai_with_image(image, selected_role):
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
                        "text": f"You are a {selected_role.lower()}. I've uploaded an image of a clothing item. Please provide your advice on whether I should keep or return this item, along with a justification for your decision. If you are a fashion stylist, consider factors like color theory and texture in your response."
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

st.title("GPT-4 Fashion Advisor")
st.write("Upload an image and get fashion advice from GPT-4.")
uploaded_image = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
role = st.radio("Select a role", ("Fashion Stylist", "Mother"))

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    response = ask_openai_with_image(image, role)
    st.write(response)