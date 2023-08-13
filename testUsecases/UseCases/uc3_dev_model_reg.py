import sys
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')
import test_framework_v2 as tfv2
import requests


def step1():
    print("Step 1- D:1 request the menu actions from C:1 using Aries RFC 0509. ")
    #get consortium connection
    url = 'http://localhost:8201/connections'
    headers = {'accept': 'application/json'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        connections = data.get('results', [])
        
        consortium_connection_id = None
        for connection in connections:
            if connection.get('alias') == 'consortium':
                consortium_connection_id = connection.get('connection_id')
                break
        
        if consortium_connection_id:
            print(f"Consortium Connection ID: {consortium_connection_id}")
        else:
            print("No connection with alias 'consortium' found.")
    else:
        print(f"Request failed with status code: {response.status_code}")

    #request menu action
    url = f'http://localhost:8201/action-menu/{consortium_connection_id}/request'
    headers = {'accept': 'application/json'}

    response = requests.post(url, headers=headers, data='')

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Request failed with status code: {response.status_code}")



def step2():
    print("Step 2- D:1 selects “Register Device Model” along with the information requested by the associated form which includes Name, Description, Features array, Images array, and WoT file. ")

def step3():
    print("Step 3- C:1 generates a DeviceModelID and anchors the information into DT Ledger. ")
    url = "http://localhost:3025/regdevmodel"
    payload = {"string": "devmodel"}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Hash sent successfully to Fabric!")
    else:
        print("Failed to send string to the server.")

def step4():
    print("Step 4- C:1 loads the WoT file to the consortium source control. ")

def step5():
    print("Step 5- C:1 loads the images and feature information to the Marketplace App. ")

def step6():
    print("Step 6- C:1 uses Aries RFC 009523 to send the deviceModelID along with DeviceName to O:1. ")


def main():
    tfv2.time_execution(step1)
    tfv2.time_execution(step2)
    tfv2.time_execution(step3)
    tfv2.time_execution(step4)
    tfv2.time_execution(step5)
    tfv2.time_execution(step6)


if __name__ == "__main__":
    main()