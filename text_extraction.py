import streamlit as st
import pandas as pd
import base64
from together import Together
from extractor import process_image_with_together
import io
import re
from text_mine import extract_data_flexible




# Together API client initialization
client = Together(api_key="21c8753437eb9ce5822db4ee270abea087cc4ab2e31f59401f8ee91d1973aa62")

# Prompt for extracting key-value pairs
getDescriptionPrompt = """extract date,rate,quantity,Amount,Product. date is alway in dd-mm-yyyy. Give output in key value always"""

# Helper function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Streamlit app UI
st.title("Invoice Data Extraction App")

uploaded_file = st.file_uploader("Upload an image of the invoice", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Encode the uploaded image
    base64_image = base64.b64encode(uploaded_file.read()).decode("utf-8")
    result = process_image_with_together(client,base64_image,getDescriptionPrompt)

    st.write(result)

    data = extract_data_flexible(result)
    
    st.write(data)

    # Define the columns and create a DataFrame
    df = pd.DataFrame([data])

    # Display the DataFrame
    st.subheader("Extracted Data:")
    st.dataframe(df)

    # Download options
    st.subheader("Download Extracted Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download as CSV", data=csv, file_name="extracted_data.csv", mime="text/csv")

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")

    # Provide download option in Streamlit
    st.download_button(
        label="Download as Excel",
        data=excel_buffer.getvalue(),
        file_name="extracted_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )