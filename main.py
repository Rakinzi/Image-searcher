from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from Searcher import ImageSearcher
from threading import Thread

DB_CONNECTION = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"
import shutil
from flask_cors import CORS

import json

secret_key = os.urandom(32)
secret_key = secret_key.hex()
app = Flask(__name__)
CORS(app)
app.secret_key = secret_key

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello'


# @app.route('/search_images', methods=['POST'])
# def search_images():
#     search_query = request.form['search']  # Retrieve the search query from the POST data
#     searcher = ImageSearcher(DB_CONNECTION)
#     urls = searcher.search(search_query)
#     destination_dir = "static/"
#
#     copied_files_info = []
#
#     for file_url in urls:
#         # Get file name from URL
#         file_name = os.path.basename(file_url)
#
#         # Construct destination file path
#         destination_file_path = os.path.join(destination_dir, file_name)
#
#         # Copy the file to the new location
#         shutil.copyfile(file_url, destination_file_path)
#
#         # Get file information
#         modification_date = os.path.getmtime(destination_file_path)
#         file_format = os.path.splitext(file_name)[1].lstrip('.')
#
#         file_info = {
#             'Image URL': file_url,
#             'Date Modified': modification_date,
#             'Format': file_format,
#             'Moved URL':  destination_file_path # Update this as needed
#         }
#
#         copied_files_info.append(file_info)
#     print(copied_files_info)
#     return jsonify(copied_files_info)

@app.route('/get_images', methods=['GET'])
def get_images():
    searcher = ImageSearcher(DB_CONNECTION)
    image_files, searched_image_status = searcher.get_image_metadata()
    print(len(image_files))
    if searched_image_status == True:
        seeding_thread = Thread(target=searcher.seed, args=(image_files,))
        seeding_thread.start()
    return jsonify(image_files)


@app.route('/search_results/<query>')
def search_results(query):
    return f'Search results for: {query}'


@app.route('/serve_images', methods=['POST'])
def serve_images():
    if request.method == 'POST':
        if 'image' in request.files and 'image_details' in request.form:
            try:
                # Parse JSON from the request form
                image_details = json.loads(request.form.get('image_details'))

                # Retrieve the image file
                image_file = request.files['image']

                # Read the image data and retrieve metadata
                image_data = image_file.read()
                mime_type = image_file.content_type
                image_filename = image_file.filename

                # Extract additional data from image details
                user_id = image_details['userId']
                image_format = mime_type.split('/')[1]
                image_date = image_details['creationDate']

                # Implement your ImageSearcher logic here
                searcher = ImageSearcher(db_connection=DB_CONNECTION)
                processor = searcher.seed_one_image(
                    image_uri=image_filename, image_format=image_format,
                    image_data=image_data, uuid=user_id, image_date=image_date
                )

                # Check the processor result
                if processor != 0:
                    images = searcher.get_inserted_images()
                    images = images['ids']
                    return jsonify({'images': images, 'status': True}), 200
                else:
                    return jsonify({'images': None, 'status': False}), 400
            except Exception as e:
                print(f"Error: {e}")
                return jsonify({'images': None, 'status': False, 'message': 'Failed'}), 400
        else:
            print("No file uploaded")
    return 'Okay'


@app.route('/search_images', methods=['POST'])
def search_for_images():
    if request.method == 'POST':
        data = request.get_json()
        if 'query' in data and 'uid' in data:
            query = data['query']
            uid = data['uid']
            searcher = ImageSearcher(DB_CONNECTION)
            images = searcher.search_one_image(query=query, uuid=uid)
            return jsonify(images)


# if __name__ == '__main__':
#     app.run(debug=True, host="0.0.0.0")
