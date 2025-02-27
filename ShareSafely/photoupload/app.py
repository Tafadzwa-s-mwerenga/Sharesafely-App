import os
from azure.storage.blob import BlobServiceClient
from flask import Flask, request

app = Flask(__name__)

# Retrieve the connection string from environment variable or assign directly (for testing)
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING') or "DefaultEndpointsProtocol=https;AccountName=photosappstoragepost;AccountKey=z0CnkOBMmN8/IcOIIdMyoPnKI9Bs9cteU0Hm379eWqQZkw4AfZmAPfAaSqBbQr5/WRnCVnny2CzZ+AStEtv+kg==;EndpointSuffix=core.windows.net"

container_name = "photos"

# Create a blob service client
blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str)

try:
    container_client = blob_service_client.get_container_client(container=container_name)
    container_client.get_container_properties()
except Exception:
    container_client = blob_service_client.create_container(container_name)

@app.route("/")
def view_photos():
    return '''
        <h1>Upload new File</h1>
        <form method="post" action="/upload-photos" enctype="multipart/form-data">
            <input type="file" name="photos" multiple>
            <input type="submit">
        </form>
    '''

@app.route("/upload-photos", methods=["POST"])
def upload_photos():
    filenames = ""

    for file in request.files.getlist("photos"):
        try:
            container_client.upload_blob(file.filename, file)  # Upload the file
            filenames += file.filename + "<br /> "
        except Exception as e:
            print(e)
            print("Ignoring duplicate filenames")
    
    return "<p>Uploaded: <br />{}</p>".format(filenames)

if __name__ == "__main__":
    app.run(debug=True)
