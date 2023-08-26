import requests
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')
import test_framework_v2 as tfv2
import datetime
import time
import json


CRED_FORMAT_INDY = "indy"
CRED_PREVIEW_TYPE = "https://didcomm.org/issue-credential/2.0/credential-preview"


def step1():
    print("\nStep 1- D:1 makes an introduction using Aries RFC0028 to O:1 passing the OOB along with goal code. ")
    #get consortium pub did
    url = 'http://0.0.0.0:8181/wallet/did/public'
    headers = { 'accept': 'application/json' }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        #print(response_data)
        pub_did = response_data["result"]["did"]
    else:
        return response.status_code
    

    url = 'http://0.0.0.0:8201/connections?alias=oem_egw'
    headers = {'accept': 'application/json'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Request failed with status code {response.status_code}")

    first_result = data["results"][0]
    dave_connection_id = first_result["connection_id"]
    #send consortium pub did from dave to oem egw
    url = f'http://0.0.0.0:8201/connections/{dave_connection_id}/send-message'
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    data = {"content": pub_did}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        #print("Message sent successfully")
        return pub_did
    else:
        #print("Failed to send message")
        print("Response:", response.text)

def step2(cons_pub_did):
    print("\nStep 2- O:1 uses the OOB to connect to C:1. ")
    #Implicit invitation from oem egw to consortium
    url = 'http://0.0.0.0:8061/didexchange/create-request'
    params = { 'their_public_did': cons_pub_did, "alias": "consortium" }
    headers = { 'accept': 'application/json' }

    response = requests.post(url, params=params, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
        return response.status_code

def step3():
    print("\nStep 3- C:1 recognizes the goal code UUID and recognizes it refers to the ongoing OEM enrollment and updates the previously entered Agent Table with the OEM’s public DID. ")
    #get oem pub did
    url = 'http://0.0.0.0:8061/wallet/did/public'
    headers = { 'accept': 'application/json' }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        #print(response_data)
        oem_pub_did = response_data["result"]["did"]
    else:
        return response.status_code
    
    dbname = "postgres"
    user = "postgres"
    password = "mysecretpassword"
    host = "localhost"
    port = "5432"

    try:
        connection = psycopg2.connect( dbname=dbname,user=user,password=password,host=host,port=port)
        #print("Connection established successfully!")

        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        create_table_query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS agent_table (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent TEXT
            )
        """)
        cursor.execute(create_table_query)
        insert_query = sql.SQL("""
            INSERT INTO agent_table (agent)
            VALUES (%s)
        """)
        connection_value = oem_pub_did
        cursor.execute(insert_query, (connection_value,))
        connection.commit()

        cursor.close()

    except psycopg2.Error as e:
        print("Error:", e)

    finally:
        if connection:
            connection.close()
            #print("Connection closed.")

def step4():
    print("\nStep 4- C:1 proposes O:1 the Enrollment VC which defines the proofs (e.g., documents) O:1 must submit so C:1 can assess the OEM trustworthiness. ")
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
def step5():
    print("\nStep 5- O:1 provides the proofs to C:1. ")

def step6(connection_id):
    print("\nStep 6- Upon validating the submitted proofs, C:1 sends a message to O:1 to generate its ecosystem ledger credentials. ")

    base_url = 'http://localhost:8181/connections/'

    url = f'{base_url}{connection_id}/send-message'

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    data = {
        "content": "Generate ledger credentials"
    }

    response = requests.post(url, headers=headers, json=data)

    #print(response.status_code)
    #print(response.json())

def step7():
    print("\nStep 7- O:1 requests the consortium a X.509 certificate. ")

def step8():
    print("\nStep 8- O:1 makes an enrollment request. ")

def step9(connection_id):
    print("\nStep 9- O:1 sends an acknowledgment to C:1 to indicate ledger successful enrollment. ")
    base_url = 'http://localhost:8061/connections/'

    url = f'{base_url}{connection_id}/send-message'

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    data = {
        "content": "Generate ledger credentials"
    }

    response = requests.post(url, headers=headers, json=data)

    #print(response.status_code)
    #print(response.json())

def step10():
    print("\nStep 10- C:1 sends the “Enrollment VC” to O:1 and expires the OOB. ")
    #get cons connection of oem
    url = 'http://localhost:8181/connections'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        connection_id = None
        
        for result in data.get('results', []):
            if result.get('their_label') == 'oem.egw.agent':
                connection_id = result.get('connection_id')
                break  # Stop searching once the desired connection is found
        
        if connection_id:
            print(f"Connection ID for 'oem.egw.agent': {connection_id}")
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
            #print("Enrollment VC ID:", enrollment_vc_id)
            print("")
        else:
            print("No Enrollment VC ID found.")
    else:
        print(f"Request failed with status code: {response.status_code}")
    #send offer to OEM from consortium
    url = 'http://localhost:8181/issue-credential/send-offer'
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    connection_id = connection_id
    cred_def_id = enrollment_vc_id

    data = {
        "auto_issue": True,
        "auto_remove": True,
        "comment": "string",
        "connection_id": connection_id,
        "cred_def_id": cred_def_id,
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
        #print(response_data)
    else:
        #print(f"Request failed with status code: {response.status_code}")
        print("")

def main():
    cons_pub_did = tfv2.time_execution(step1)
    tfv2.time_execution(step2, cons_pub_did)
    tfv2.time_execution(step3)
    connect = tfv2.time_execution(step4)
    tfv2.time_execution(step5)
    tfv2.time_execution(step6, connect)
    tfv2.time_execution(step7)
    tfv2.time_execution(step8)
    tfv2.time_execution(step9, connect)
    tfv2.time_execution(step10)


if __name__ == "__main__":
    main()