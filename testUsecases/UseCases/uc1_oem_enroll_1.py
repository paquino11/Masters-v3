import subprocess
import os
import sys
import requests
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')  # Add the path to the directory containing test.py
import test_framework_v2 as tfv2
import AgentsDeployment.deploy_agents as agents

def step1():
    print("\nStep 1- Dave taps the “Enroll OEM” button on the consortium’s marketing website.")

def step2():
    print("\nStep 2- The marketing website makes a call to C:1 Admin API to requests an OOB URI.")
    url = 'http://0.0.0.0:8181/out-of-band/create-invitation'
    params = { 'auto_accept': 'true', 'multi_use': 'false' }

    headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' }

    data = { "handshake_protocols": [ "rfc23" ], "use_public_did": False }

    response = requests.post(url, params=params, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        #print("Invitation created successfully:", response_data)
        #print(response_data['invitation_url'])
        return response_data
    else:
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
        return response.text
        
def step3():
    print("\nStep 3- C:1 creates an UUID for the transaction and stores it in the “Transaction Table”.")
    

def step4():
    print("\nStep 4- C:1 creates the OOB and the goal code c2dt.consortium.enroll.OEM?UUID.")
    url = 'http://0.0.0.0:8181/out-of-band/create-invitation'
    params = { 'auto_accept': 'true', 'multi_use': 'false' }

    headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' }

    data = { "handshake_protocols": [ "rfc23" ], "use_public_did": False, "goal_code": "c2dt.consortium.enroll.OEM?UUID" }

    response = requests.post(url, params=params, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        #print(response_data)#"""['invitation_url']"""
        return response_data
    else:
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
        return response.text

def step5():
    print("\nStep 5- The marketing website redirects Dave to a new page that contains the OOB URI along with the instructions to deploy the OEM’s DIDComm Agent (O:1).")

def step6():
    print("\nStep 6- The OEM staff deploys the DIDComm and starts it up.")
    agents.deploy_oem_egw

def step7():
    print("\nStep 7- During the first boot O:1 creates its public DID.")

def step8():
    print("\nStep 8- Dave (D:1) clicks the OOB URI which opens his smart wallet via a deep link.")

def step9(invitation):
    print("\nStep 9- D:1 establishes a connection with C:1 using the OOB URI.")
    recipient_keys = invitation['invitation']['services'][0]['recipientKeys']
    invitation_id = invitation['invitation']['@id']
    service_endpoint = invitation['invitation']['services'][0]['serviceEndpoint']

    url = 'http://0.0.0.0:8201/out-of-band/receive-invitation?auto_accept=true&use_existing_connection=false'    

    headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' }

    data = {
        "@id": invitation_id,
        "@type": "https://didcomm.org/out-of-band/1.1/invitation",
        "handshake_protocols": [
            "https://didcomm.org/didexchange/1.0"
        ],
        "services": [
            {
                "id": "string",
                "recipientKeys": recipient_keys,
                "serviceEndpoint": service_endpoint,
                "type": "did-communication"
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        #print(response_data)#"""['invitation_url']"""
        return response_data
    else:
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
        return response.text

def step10():
    print("\nStep 10- The Consortium’s DIDComm Agent (C:1) identifies the goal code UUID and recognizes that it refers to the ongoing OEM enrollment and creates a new entry into the Agent Table. ")

def step11():
    print("\nStep 11- D:1 establishes a connection with O:1 using an implicit invitation which is known to Dave because he has access to the O:1")
    # get OEM EGW Public did
    url = 'http://0.0.0.0:8061/wallet/did/public'
    headers = { 'accept': 'application/json' }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        #print(response_data)
        pub_did = response_data["result"]["did"]
    else:
        return response.status_code
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
    #Implicit invitation from dave to oem egw
    url = 'http://0.0.0.0:8201/didexchange/create-request'
    params = { 'their_public_did': pub_did }
    headers = { 'accept': 'application/json' }

    response = requests.post(url, params=params, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
        return response.status_code


def main():
    tfv2.time_execution(step1)
    tfv2.time_execution(step2)
    tfv2.time_execution(step3)
    response = tfv2.time_execution(step4)
    tfv2.time_execution(step5)
    tfv2.time_execution(step6)
    tfv2.time_execution(step7)
    tfv2.time_execution(step8)
    tfv2.time_execution(step9, response[0])
    tfv2.time_execution(step10)
    tfv2.time_execution(step11)



if __name__ == "__main__":
    main()