from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import os
from urllib.parse import quote_plus

# Azure Storage Configuration
STORAGE_ACCOUNT_NAME = "techwebfiles"
STORAGE_ACCOUNT_KEY = "GtDpjhcaGwk+myqkhfC9YutN8o2tDBh+PlHbZ7PAwY2p6OQNsDXaB58cWIA8RzBcdYu2Vp6biU7H+AStuf9cwg=="
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=techwebfiles;AccountKey=GtDpjhcaGwk+myqkhfC9YutN8o2tDBh+PlHbZ7PAwY2p6OQNsDXaB58cWIA8RzBcdYu2Vp6biU7H+AStuf9cwg==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "files"

# Initialize Flask App
app = Flask(__name__)
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

@app.route("/upload", methods=["POST"])
def upload_file():
    """Endpoint to upload a file to Azure Blob Storage."""
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected for upload"}), 400

    try:
        # blob name
        blob_name = file.filename

        # blob client
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)

        # Upload the file stream
        blob_client.upload_blob(file.stream, overwrite=True)

        # Verify upload by checking blob existence
        if not blob_client.exists():
            return jsonify({"error": "File upload failed. Blob does not exist in storage."}), 500

        # Generate the SAS URL
        sas_url = generate_blob_sas_url(blob_name)
        return jsonify({"message": "File uploaded successfully", "url": sas_url})

    except Exception as e:
        return jsonify({"error": f"Error uploading file: {str(e)}"}), 500

def generate_blob_sas_url(blob_name):
    """Generate a Shared Access Signature (SAS) URL for the uploaded file."""
    try:
        # blob-level SAS token
        sas_token = generate_blob_sas(
            account_name=STORAGE_ACCOUNT_NAME,
            container_name=CONTAINER_NAME,
            blob_name=blob_name,
            account_key=STORAGE_ACCOUNT_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=24)  # Link valid for 1 hour
        )

    
        blob_name_encoded = quote_plus(blob_name)

        # Return complete SAS URL
        return f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{blob_name_encoded}?{sas_token}"
    except Exception as e:
        raise Exception(f"Error generating SAS URL: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)
