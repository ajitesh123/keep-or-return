# Import the necessary libraries
import streamlit as st
import openai
import base64
from PIL import Image
import io
import requests
import os
import concurrent.futures

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
def ask_openai_with_image(image):
    # Encode the uploaded image to base64
    base64_image = encode_image_to_base64(image)
    
    # Create the payload with the base64 encoded image
    outfit_advice_payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Based on color theory, texture, and material, suggest whether the outfit is a keep or a return."
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base
                    }
                ]
            }
        ],
        "max_tokens": 4095
    }
    mom_advice_payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Act as my mother and give a suggestion on whether to keep or return this outfit, taking emotion into account."
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
    responses = parallel_request([outfit_advice_payload, mom_advice_payload])
    return responses
    
    # Send the request to the OpenAI API
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {openai.api_key}"},
        json=payload
    )
    
    # Check if the request was successful
    if response.status
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
    st.title("AI Fashion Advisor")
    image = st.file_uploader("Upload an image of the outfit", type=["jpg", "png"])
    if image:
        image = Image.open(image)
        responses = ask_openai_with_image(image)
        st.write("AI's Outfit Advice:", responses[0])
        st.write("Mom's Advice:", responses[1])
if __name__ == "__main__":
    main()

# Launch the app
iface.launch()