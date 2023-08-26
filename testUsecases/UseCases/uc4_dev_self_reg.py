import sys, requests, time, json, uuid
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')
import test_framework_v2 as tfv2
import AgentsDeployment.deploy_agents as agents


CRED_FORMAT_INDY = "indy"
CRED_PREVIEW_TYPE = "https://didcomm.org/issue-credential/2.0/credential-preview"

LEDGER_URL="http://dev.greenlight.bcovrin.vonx.io"


def step1_1():
    print("Step 1- The OEM integrates the consortium firmware libraries. ")

def step2_1():
    print("Step 2- During first boot, the EGW executes a script that boots egw:1.  ")
    agents.deploy_egw()

def step3_1():
    print("Step 3- egw:1 creates the public DID. ")
    url = 'http://0.0.0.0:8181/wallet/did/create'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        print("Response:", response_data)
    else:
        print("Request failed with status code:", response.status_code)
    time.sleep(2)

def step4_1():  
    print("Step 4- egw:1 utilizes the configuration files with the OEM’s public DID and implicit connection invitation to O:1 using goal c2dt.consortium.registerdevice?DID. ")

    #get oem egwpub did
    url = 'http://0.0.0.0:8061/wallet/did/public'
    headers = {
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        print("Response:", response_data)
        oem_did = response_data['result']['did']
    else:
        print("Request failed with status code:", response.status_code)

    #Implicit invitation from egw to oem egw
    url = 'http://0.0.0.0:8091/didexchange/create-request'
    params = { 'their_public_did': oem_did, "alias": "oem_egw" }
    headers = { 'accept': 'application/json' }

    response = requests.post(url, params=params, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
        return response.status_code

def step5_1():
    print("Step 5- O:1 sends egw:1 the Genesis VC proposal using Aries RFC 045324. ")
    #get oem connection of cons
    url = 'http://localhost:8061/connections'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        connection_id = None
        
        for result in data.get('results', []):
            if result.get('alias') == 'consortium':
                connection_id = result.get('connection_id')
                break  # Stop searching once the desired connection is found
        
        if connection_id:
            print(f"Connection ID for 'consortium': {connection_id}")
        else:
            print("No connection found for 'oem.egw.agent'")
    else:
        print(f"Request failed with status code: {response.status_code}")
    #get VC id of enrollment
    url = 'http://localhost:8181/credential-definitions/created'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        credential_definition_ids = data['credential_definition_ids']
        enrollment_vc_id = None
        for cred_id in credential_definition_ids:
            if cred_id.endswith('Enrollment_VC'):
                enrollment_vc_id = cred_id
                break
        if enrollment_vc_id:
            print("Enrollment VC ID:", enrollment_vc_id)
            print("")
        else:
            print("No Enrollment VC ID found.")
    else:
        print(f"Request failed with status code: {response.status_code}")
    #send offer to OEM from consortium
    url = 'http://localhost:8061/issue-credential/send-proposal'
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    connection_id = connection_id
    cred_def_id = enrollment_vc_id

    data = {
            "auto_remove": True,
            "comment": "string",
            "connection_id": connection_id,
            "cred_def_id": cred_def_id ,
            "credential_preview": {
                        "@type": "issue-credential/1.0/credential-preview",
                        "attributes": [
                            {
                                "mime-type": "image/jpeg",
                                "name": "name",
                                "value": "Bosch"
                            },
                            {
                                "mime-type": "image/jpeg",
                                "name": "type",
                                "value": "OEM"
                            },
                            {
                                "mime-type": "image/jpeg",
                                "name": "enrollDate",
                                "value": str(int(time.time()))
                            },
                            {
                                "mime-type": "image/jpeg",
                                "name": "timestamp",
                                "value": str(int(time.time()))
                            }
                        ]
                    },
            "trace": True
            }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        print("it was proposed")
        return connection_id
    else:
        #print(f"Request failed with status code: {response.status_code}")
        print("")

def step6_1():
    print("Step 6- O:1 registers EGW into the DT ledger and creates the EGW’s DT Ledger client user credentials which are required because the EGW must be able to write to the ledger. ")
    url = "http://localhost:3025/regdataset"
    payload = {"string": "EGWA AGent"}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Aries Agent succesfully created!")
    else:
        print("Failed to send string to the server.")

def step7_1():
    print("Step 7- O:1 makes the SD available for the sale in the Marketplace App by associating the “buy button” URL as the OEM’s OOB Link with the goal c2dt.consortium.buydevice, along with the sale information.  ")

def step8_1():
    print("Step 8- O:1 sends egw:1 the Genesis VC. ")
    #get oem egwpub did
    url = 'http://0.0.0.0:8061/wallet/did/public'
    headers = {
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        print("Response:", response_data)
        oem_did = response_data['result']['did']
    else:
        print("Request failed with status code:", response.status_code)

    #Implicit invitation from egw to oem egw
    url = 'http://0.0.0.0:8091/didexchange/create-request'
    params = { 'their_public_did': oem_did, "alias": "oem_egw" }
    headers = { 'accept': 'application/json' }

    response = requests.post(url, params=params, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
        return response.status_code



def step1_2():
    print("Step 1- The OEM integrates the consortium firmware libraries. ")

def step2_2():
    print("Step 2- During the first boot, the SD executes a script that boots sd:1. ")
    agents.deploy_sd()

def step3_2():
    print("Step 3- sd:1 generates an UUID. ")
    # Generate a random UUID
    random_uuid = uuid.uuid4()
    print("UUID:", random_uuid)

def step4_2():
    print("Step 4- sd:1 utilizes the configuration files that were set by the OEM and sends an implicit invitation to O:1 to establish a connection with the goal c2dt.consortium.registerdevice?UUID. ")
    #get oem egwpub did
    url = 'http://0.0.0.0:8061/wallet/did/public'
    headers = {
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        print("Response:", response_data)
        oem_did = response_data['result']['did']
    else:
        print("Request failed with status code:", response.status_code)

    #Implicit invitation from egw to oem egw
    url = 'http://0.0.0.0:8091/didexchange/create-request'
    params = { 'their_public_did': oem_did, "alias": "oem_egw" }
    headers = { 'accept': 'application/json' }

    response = requests.post(url, params=params, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
        return response.status_code

def step5_2():
    print("Step 5- O:1 sends sd:1 the Genesis VC proposal. ")
#get oem connection of cons
    url = 'http://localhost:8061/connections'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        connection_id = None
        
        for result in data.get('results', []):
            if result.get('alias') == 'consortium':
                connection_id = result.get('connection_id')
                break  # Stop searching once the desired connection is found
        
        if connection_id:
            print(f"Connection ID for 'consortium': {connection_id}")
        else:
            print("No connection found for 'oem.egw.agent'")
    else:
        print(f"Request failed with status code: {response.status_code}")
    #get VC id of enrollment
    url = 'http://localhost:8181/credential-definitions/created'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        credential_definition_ids = data['credential_definition_ids']
        enrollment_vc_id = None
        for cred_id in credential_definition_ids:
            if cred_id.endswith('Enrollment_VC'):
                enrollment_vc_id = cred_id
                break
        if enrollment_vc_id:
            print("Enrollment VC ID:", enrollment_vc_id)
            print("")
        else:
            print("No Enrollment VC ID found.")
    else:
        print(f"Request failed with status code: {response.status_code}")
    #send offer to OEM from consortium
    url = 'http://localhost:8061/issue-credential/send-proposal'
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    connection_id = connection_id
    cred_def_id = enrollment_vc_id

    data = {
            "auto_remove": True,
            "comment": "string",
            "connection_id": connection_id,
            "cred_def_id": cred_def_id ,
            "credential_preview": {
                        "@type": "issue-credential/1.0/credential-preview",
                        "attributes": [
                            {
                                "mime-type": "image/jpeg",
                                "name": "name",
                                "value": "Bosch"
                            },
                            {
                                "mime-type": "image/jpeg",
                                "name": "type",
                                "value": "OEM"
                            },
                            {
                                "mime-type": "image/jpeg",
                                "name": "enrollDate",
                                "value": str(int(time.time()))
                            },
                            {
                                "mime-type": "image/jpeg",
                                "name": "timestamp",
                                "value": str(int(time.time()))
                            }
                        ]
                    },
            "trace": True
            }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        print("it was proposed")
        return connection_id
    else:
        #print(f"Request failed with status code: {response.status_code}")
        print("")

def step6_2():
    print("Step 6- O:1 register devices into the DT ledger. ")
    url = "http://localhost:3025/regdataset"
    payload = {"string": "SD AGent"}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Aries Agent succesfully created!")
    else:
        print("Failed to send string to the server.")

def step7_2():
    print("Step 7- O:1 makes the SD available for the sale in the Marketplace App by associating the “buy button” URL as the OEM’s OOB Link with the goal c2dt.consortium.buydevice, along with the sale information. ")

def step8_2():
    print("Step 8- O:1 sends sd:1 the Genesis VC. ")
#get oem connection of cons
    url = 'http://localhost:8061/connections'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        connection_id = None
        
        for result in data.get('results', []):
            if result.get('alias') == 'consortium':
                connection_id = result.get('connection_id')
                break  # Stop searching once the desired connection is found
        
        if connection_id:
            print(f"Connection ID for 'consortium': {connection_id}")
        else:
            print("No connection found for 'oem.egw.agent'")
    else:
        print(f"Request failed with status code: {response.status_code}")
    #get VC id of enrollment
    url = 'http://localhost:8181/credential-definitions/created'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        credential_definition_ids = data['credential_definition_ids']
        enrollment_vc_id = None
        for cred_id in credential_definition_ids:
            if cred_id.endswith('Enrollment_VC'):
                enrollment_vc_id = cred_id
                break
        if enrollment_vc_id:
            print("Enrollment VC ID:", enrollment_vc_id)
            print("")
        else:
            print("No Enrollment VC ID found.")
    else:
        print(f"Request failed with status code: {response.status_code}")
    #send offer to OEM from consortium
    url = 'http://localhost:8061/issue-credential/send-proposal'
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    connection_id = connection_id
    cred_def_id = enrollment_vc_id

    data = {
            "auto_remove": True,
            "comment": "string",
            "connection_id": connection_id,
            "cred_def_id": cred_def_id ,
            "credential_preview": {
                        "@type": "issue-credential/1.0/credential-preview",
                        "attributes": [
                            {
                                "mime-type": "image/jpeg",
                                "name": "name",
                                "value": "Bosch"
                            },
                            {
                                "mime-type": "image/jpeg",
                                "name": "type",
                                "value": "OEM"
                            },
                            {
                                "mime-type": "image/jpeg",
                                "name": "enrollDate",
                                "value": str(int(time.time()))
                            },
                            {
                                "mime-type": "image/jpeg",
                                "name": "timestamp",
                                "value": str(int(time.time()))
                            }
                        ]
                    },
            "trace": True
            }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        print("it was proposed")
        return connection_id
    else:
        #print(f"Request failed with status code: {response.status_code}")
        print("")





def main():
    print("EGW SELF REG")
    tfv2.time_execution(step1_1)
    tfv2.time_execution(step2_1)
    tfv2.time_execution(step3_1)
    tfv2.time_execution(step4_1)
    tfv2.time_execution(step5_1)
    tfv2.time_execution(step6_1)
    tfv2.time_execution(step7_1)
    tfv2.time_execution(step8_1)

    print("sd SELF REG")
    tfv2.time_execution(step1_2)
    tfv2.time_execution(step2_2)
    tfv2.time_execution(step3_2)
    tfv2.time_execution(step4_2)
    tfv2.time_execution(step5_2)
    tfv2.time_execution(step6_2)
    tfv2.time_execution(step7_2)
    tfv2.time_execution(step8_2)

if __name__ == "__main__":
    main()