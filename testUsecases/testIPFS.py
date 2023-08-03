import ipfsApi
import requests
import json


def write_to_ipfs(file_path):
    try:
        api = ipfsApi.Client('127.0.0.1', 5001)  # Connect to the IPFS daemon
        res = api.add(file_path)  # Add the file to IPFS
        file_hash = res[0]['Hash']  # Access the first element in the list
        print("File uploaded to IPFS with hash:", file_hash)
    except Exception as e:
        print("An error occurred:", str(e))
    return file_hash


def delete_from_ipfs(file_hash):
    try:
        # Check if the file is pinned
        check_url = f"http://127.0.0.1:5001/api/v0/pin/ls?arg={file_hash}"
        check_response = requests.get(check_url)
        check_data = json.loads(check_response.text)
        
        if 'Keys' not in check_data:
            print("File is not pinned or pinned indirectly.")
            return
        
        # Remove the pin for the file
        remove_url = f"http://127.0.0.1:5001/api/v0/pin/rm?arg={file_hash}"
        remove_response = requests.post(remove_url)
        
        if remove_response.status_code == 200:
            print("File successfully deleted from IPFS.")
        else:
            print("An error occurred while deleting the file from IPFS.")
            print("Response:", remove_response.text)
    except Exception as e:
        print("An error occurred:", str(e))
# Example usage
file_path = "/home/pedro/Desktop/Aries-Agents/testUsecases/ipfs.txt"
ipfshash = write_to_ipfs(file_path)


delete_from_ipfs(ipfshash)