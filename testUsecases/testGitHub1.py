import requests
import base64
import time


access_token = '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'

# Set the repository details
owner = 'paquino11'
repo = 'wot_files'

# Set the branch where you want to add the file
branch = 'main'  # Replace with the desired branch name

# Set the file details
file_path = 'home/pedro/Desktop/Masters-v3/testUsecases/wotfile.txt'
file_path1 = '/home/pedro/Desktop/Masters-v3/testUsecases/wotfile.txt'
# Read the content of the file
with open(file_path1, 'r') as file:
    file_content = file.read()

import datetime

current_timestamp = str(datetime.datetime.now())

print(current_timestamp)

url = f'https://api.github.com/repos/{owner}/{repo}/contents/wotfile{current_timestamp}.txt'

# Set the headers
headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Prepare the request payload
data = {
    'message': 'Add file via API',
    'content': file_content
}

# Encode the file content as base64
import base64
data['content'] = base64.b64encode(data['content'].encode()).decode()

# Send the POST request to create the file
response = requests.put(url, headers=headers, json=data)

# Check the response
if response.status_code == 201:
    print('File added successfully!')
else:
    print(f'Failed to add file. Status code: {response.status_code}, Error message: {response.json()["message"]}')

