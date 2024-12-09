import streamlit as st
import pandas as pd
import base64
from together import Together






def process_image_with_together(api_client, base64_image, prompt):
    """
    Processes an image using Together's API and extracts data based on a provided prompt.

    Args:
        api_client (Together): Initialized Together API client.
        base64_image (str): Base64-encoded image string.
        prompt (str): Instruction prompt to extract specific data.

    Returns:
        str: The result extracted from the image as a string.
    """
    # Create a streaming response from the Together API
    stream = api_client.chat.completions.create(
        model="meta-llama/Llama-Vision-Free",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        stream=True,
    )

    result = ""  

    for chunk in stream:
        if chunk.choices and len(chunk.choices) > 0:
            delta = getattr(chunk.choices[0], "delta", None)
            content = getattr(delta, "content", None)
            if content:
                result += content  
            
        else:
            print("Invalid chunk structure")

    return result
