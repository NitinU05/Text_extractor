def extract_data_flexible(text):
    """
    Extracts key-value pairs or comma-separated data from the given text, handling additional formatting like emphasized values.
    
    Args:
        text (str): The input text to parse.
    
    Returns:
        dict: A dictionary with extracted data.
    """
    # Define possible keys for structured format
    key_aliases = {
        "Bill_Date": ["Date"],
        "Rate": ["Rate", "Rate/Ltr"],
        "Quantity": ["Quantity", "Qantity", "Volume", "Volume (Ltr)", "Qty"],
        "Amount": ["Amount", "Amt", "Rs."],
        "Product": ["Product"]
    }

    # Initialize the result dictionary with None for each key
    extracted_data = {key: None for key in key_aliases}

    # Check if the text is in comma-separated format
    if "," in text and ":" not in text:
        # Handle comma-separated format
        values = [v.strip() for v in text.split(",")]
        keys = list(extracted_data.keys())  # Use the dictionary's keys
        for key, value in zip(keys, values):
            extracted_data[key] = value
    else:
        # Handle structured text format
        lines = text.split("\n")
        for line in lines:
            if ":" in line:
                key_part, value_part = line.split(":", 1)
                key_part = key_part.strip().lower()
                value_part = value_part.strip()

                # Remove any emphasized characters like ** or units like Ltr
                value_part = value_part.strip("*").strip()
                if "ltr" in value_part.lower():
                    value_part = value_part.lower().replace("ltr", "").strip()
                if "rs." in value_part.lower():
                    value_part = value_part.lower().replace("rs.", "").strip()

                # Match the key_part against known aliases
                for key, aliases in key_aliases.items():
                    if any(alias.lower() in key_part for alias in aliases):
                        extracted_data[key] = value_part
                        break

    return extracted_data