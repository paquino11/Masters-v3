import requests
import base64
import time

GREEN = '\033[1;32m'
RESET = '\033[0m'

total_start_time = time.time()
# Set your GitHub access token
access_token = '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'

# Set the repository details
owner = 'paquino11'
repo = 'wot_files'

# Set the branch where you want to add the file
branch = 'main'  # Replace with the desired branch name

# Set the file details
file_path = 'home/pedro/Desktop/Aries-Agents/testUsecases/wotfile.txt'
file_path1 = '/home/pedro/Desktop/Aries-Agents/testUsecases/wotfile.txt'
# Read the content of the file
with open(file_path1, 'r') as file:
    file_content = file.read()

# Set the API endpoint URL
url = f'https://api.github.com/repos/{owner}/{repo}/contents/wotfile4.txt'

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

total_end_time = time.time()
total_execution_time = round(total_end_time - total_start_time, 3)
print(f"{GREEN}\t{total_execution_time}\n{RESET}")