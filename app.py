# Import the necessary libraries
import streamlit as st
import asyncio
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
def ask_openai_with_image(base64_image, perspective):
    if perspective == "fashion_stylist":
        prompt = "I've uploaded an image of a fashion outfit. As a fashion stylist, please analyze the outfit based on color theory, texture, and material, and provide suggestions on whether to keep or return the outfit."
    elif perspective == "user_mother":
        prompt = "I've uploaded an image of a fashion outfit. As the user's mother, please analyze the outfit considering the emotional aspect and provide suggestions on whether to keep or return the outfit."
    else:
        raise ValueError("Invalid perspective provided.")

    # Create the payload with the base64 encoded image and the prompt
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
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

    # Send the request to the OpenAI API and handle the response
    # (existing code for sending the request and processing the response)
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
                        "text": "I've uploaded an image and I'd like to know what it depicts and any interesting details you can provide."
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

def app():
    st.title("Fashion Outfit Analyzer")
    uploaded_file = st.file_uploader("Upload an image of a fashion outfit", type=["jpg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Call the main function to get the verdict
        verdict = asyncio.run(main(image))
        st.write(f"Verdict: {verdict}")

if __name__ == "__main__":
    app()
async def main(image):
    # Encode the image to base64
    base64_image = encode_image_to_base64(image)

    # Initiate the two parallel LLM calls
    stylist_task = asyncio.create_task(ask_openai_with_image(base64_image, "fashion_stylist"))
    mother_task = asyncio.create_task(ask_openai_with_image(base64_image, "user_mother"))

    # Wait for both tasks to complete
    stylist_response, mother_response = await asyncio.gather(stylist_task, mother_task)

    # Analyze the responses and provide a verdict
    if analyze_stylist_response(stylist_response) and analyze_mother_response(mother_response):
        verdict = "Keep the outfit"
    else:
        verdict = "Return the outfit"

    return verdict

def analyze_stylist_response(response):
    # Analyze the response from the fashion stylist perspective
    # (Implement logic to determine if the response suggests keeping or returning the outfit)
    # Return True if the response suggests keeping the outfit, False otherwise

def analyze_mother_response(response):
    # Analyze the response from the user's mother perspective
    # (Implement logic to determine if the response suggests keeping or returning the outfit)
    # Return True if the response suggests keeping the outfit, False otherwise
