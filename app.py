# Import the necessary libraries
import streamlit as st
import openai
import base64
from PIL import Image
import io
import requests
import os

st.set_page_config(page_title="Fashion Advisor", page_icon=":dress:")
st.title("Fashion Advisor with GPT-4")
st.write("Upload an image and get advice from a fashion stylist or mother.")

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

    if role == "fashion_stylist":
        prompt = "As a fashion stylist, would you recommend keeping or returning this clothing item? Please provide a justification for your decision, considering factors like color theory, texture, and overall style."
    elif role == "mother":
        prompt = "As a mother, would you recommend keeping or returning this clothing item for your child? Please provide a justification for your decision, considering factors like practicality, comfort, and your child's needs."
    else:
        raise ValueError(f"Invalid role: {role}")

    # Create the payload with the base64 encoded image
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
    
    # Send the request to the OpenAI API
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {openai.api_key}"},
        json=payload
    )
    
    # Check if the request was successful
def parse_llm_response(response_text):
    lines = response_text.strip().split("\n")
    decision = lines[0].split(":")[1].strip().lower()
    justification = " ".join(lines[1:]).strip()
    return decision, justification

    if response.status_code == 200:
        response_json = response.json()
        print("Response JSON:", response_json)  # Print the raw response JSON
        try:
            # Attempt to extract the content text
            response_text = response_json["choices"][0]["message"]["content"]
            decision, justification = parse_llm_response(response_text)
            return decision, justification
        except Exception as e:
            # If there is an error in the JSON structure, print it
            print("Error in JSON structure:", e)
            print("Full JSON response:", response_json)
            return "Error processing the image response.", ""
    else:
        # If an error occurred, return the error message
        return f"Error: {response.text}", ""

role = st.radio("Select a role", ("Fashion Stylist", "Mother"))
role = role.lower().replace(" ", "_")

uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    decision, justification = ask_openai_with_image(image, role)
    st.subheader(f"{role.title()}'s Recommendation")
    st.write(f"Decision: {decision.capitalize()}")
    st.write(f"Justification: {justification}")