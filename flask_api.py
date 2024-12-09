from flask import Flask, render_template, request, send_file, session
import pandas as pd
import base64
import io
import os
from together import Together
from extractor import process_image_with_together
from text_mine import extract_data_flexible

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for session management

# Together API 
client = Together(api_key="21c8753437eb9ce5822db4ee270abea087cc4ab2e31f59401f8ee91d1973aa62")

# Prompt 
getDescriptionPrompt = """Extract date, rate, quantity, amount, and product. 
Date is always in dd-mm-yyyy format. Provide output in key-value pairs only."""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        files = request.files.getlist("files")
        if not files:
            return render_template("index.html", error="No files uploaded.")
        
        results = []
        dfs = []

        for file in files:
            label = file.filename
            try:
                # Encode the image
                base64_image = base64.b64encode(file.read()).decode("utf-8")

                # Process ocr
                result = process_image_with_together(client, base64_image, getDescriptionPrompt)

                # Extract data into a structured format
                data = extract_data_flexible(result)
                results.append({label: data})

                # Append the structured data to a DataFrame
                df = pd.DataFrame([data])
                dfs.append(df)

            except Exception as e:
                return render_template("index.html", error=f"Error processing {label}: {str(e)}")

        # Add all extracted data into a single DataFrame
        consolidated_df = pd.concat(dfs, ignore_index=True)

        # Save the data to the session for download routes
        session['data'] = consolidated_df.to_json()

        return render_template(
            "index.html",
            message="Files processed successfully!",
            results=results,
            show_download=True
        )

    return render_template("index.html")


@app.route("/download_csv", methods=["GET"])
def download_csv():
    # Retrieve data from session
    data = session.get('data')
    if not data:
        return "No data available for download.", 400

    # Convert JSON to DataFrame
    consolidated_df = pd.read_json(data)

    # Save DataFrame as CSV
    csv_buffer = io.BytesIO()
    consolidated_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return send_file(
        csv_buffer,
        mimetype="text/csv",
        as_attachment=True,
        download_name="extracted_data.csv",
    )


@app.route("/download_excel", methods=["GET"])
def download_excel():
    # Retrieve data from session
    data = session.get('data')
    if not data:
        return "No data available for download.", 400

    # Convert JSON to DataFrame
    consolidated_df = pd.read_json(data)

    # Save DataFrame as Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        consolidated_df.to_excel(writer, index=False, sheet_name="Sheet1")
    excel_buffer.seek(0)

    return send_file(
        excel_buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="extracted_data.xlsx",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)