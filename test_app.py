import streamlit as st
import pandas as pd
import base64
from together import Together
from extractor import process_image_with_together
import io
from text_mine import extract_data_flexible

# Together API client initialization
client = Together(api_key="21c8753437eb9ce5822db4ee270abea087cc4ab2e31f59401f8ee91d1973aa62")

# Prompt for extracting key-value pairs
getDescriptionPrompt = """Extract date, rate, quantity, amount, and product. 
Date is always in dd-mm-yyyy format. Provide output in key-value pairs only."""

# Streamlit app UI
st.title("Invoice Data Extraction App")

# Allow multiple file uploads
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
            col1, col2 = st.columns(2)
            with col1:

                st.write("Raw extraction result:")
                st.write(result)

            # Extract data into a structured format
            with col2:
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
