import streamlit as st
import pandas as pd
import base64
from together import Together
from extractor import process_image_with_together
import io
import json
from text_mine import extract_data_flexible

# Together API client initialization
client = Together(api_key="21c8753437eb9ce5822db4ee270abea087cc4ab2e31f59401f8ee91d1973aa62")

# Prompt for extracting key-value pairs
getDescriptionPrompt = """Extract date, rate, quantity, amount, and product. 
Date is always in dd-mm-yyyy format. Provide output in key-value pairs only."""

# Streamlit app UI
st.title("Invoice Data Extraction App")

# Check for query parameters
query_params = st.query_params

# Check if 'api=true' is in the query params
if "api" in query_params and query_params["api"][0] == "true":
    # Handle the API request and return JSON response

    # Check if the 'file' parameter exists (i.e., the image was uploaded)
    if "file" in query_params:
        # Convert the base64 image back to bytes
        base64_image = query_params["file"][0]

        # Process the image with Together API
        result = process_image_with_together(client, base64_image, getDescriptionPrompt)

        # Extract data into a structured format
        data = extract_data_flexible(result)

        # Return the extracted data as JSON
        st.json(data)  # This will return the data in JSON format

else:
    # Regular Streamlit file uploader UI
    uploaded_files = st.file_uploader(
        "Upload one or more images of the invoices", type=["jpg", "jpeg", "png"], accept_multiple_files=True
    )

    if uploaded_files:
        results = []
        dfs = []

        for uploaded_file in uploaded_files:
            st.write(f"Processing: {uploaded_file.name}")
            try:
                # Encode the uploaded image
                base64_image = base64.b64encode(uploaded_file.read()).decode("utf-8")

                # Process the image with Together API
                result = process_image_with_together(client, base64_image, getDescriptionPrompt)

                # Display the raw result
                st.write("Raw extraction result:")
                st.write(result)

                # Extract data into a structured format
                data = extract_data_flexible(result)
                st.write("Extracted Data:")
                st.write(data)

                # Append the structured data to a list for consolidation
                results.append(data)

                # Create a DataFrame for this file and append to dfs
                df = pd.DataFrame([data])
                dfs.append(df)

            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")

        # Consolidate all extracted data into a single DataFrame
        if dfs:
            consolidated_df = pd.concat(dfs, ignore_index=True)

            # Display the consolidated DataFrame
            st.subheader("Extracted Data from All Files:")
            st.dataframe(consolidated_df)

            # Download options
            st.subheader("Download Extracted Data")

            # CSV Download
            csv = consolidated_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download as CSV", data=csv, file_name="extracted_data.csv", mime="text/csv")

            # Excel Download
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                consolidated_df.to_excel(writer, index=False, sheet_name="Sheet1")

            st.download_button(
                label="Download as Excel",
                data=excel_buffer.getvalue(),
                file_name="extracted_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
