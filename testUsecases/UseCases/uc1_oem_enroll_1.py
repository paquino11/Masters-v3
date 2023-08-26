import subprocess
import os
import time
import sys
import requests
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/') 
import test_framework_v2 as tfv2
import AgentsDeployment.deploy_agents as agents
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import matplotlib.pyplot as plt
import numpy as np

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
        print("error")
        
def step3():
    print("\nStep 3- C:1 creates an UUID for the transaction and stores it in the “Transaction Table”.")

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
            CREATE TABLE IF NOT EXISTS transaction_table (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                connection TEXT
            )
        """)
        cursor.execute(create_table_query)
        insert_query = sql.SQL("""
            INSERT INTO transaction_table (connection)
            VALUES (%s)
        """)
        connection_value = "Sample connection"
        cursor.execute(insert_query, (connection_value,))
        connection.commit()

        cursor.close()

    except psycopg2.Error as e:
        print("Error:", e)
        print("error")

    finally:
        if connection:
            connection.close()
            #print("Connection closed.")

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
        #return response.text
        print("error")

def step5():
    print("\nStep 5- The marketing website redirects Dave to a new page that contains the OOB URI along with the instructions to deploy the OEM’s DIDComm Agent (O:1).")

def step6():
    print("\nStep 6- The OEM staff deploys the DIDComm and starts it up.")
    agents.deploy_oem_egw()

def step7():
    print("\nStep 7- During the first boot O:1 creates its public DID.")

def step8():
    print("\nStep 8- Dave (D:1) clicks the OOB URI which opens his smart wallet via a deep link.")

def step9(invitation):
    print("\nStep 9- D:1 establishes a connection with C:1 using the OOB URI.")
    recipient_keys = invitation['invitation']['services'][0]['recipientKeys']
    invitation_id = invitation['invitation']['@id']
    service_endpoint = invitation['invitation']['services'][0]['serviceEndpoint']

    url = 'http://0.0.0.0:8201/out-of-band/receive-invitation?auto_accept=true&use_existing_connection=false&alias=consortium'    

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
        #return response.text
        print("error")

def step10():
    print("\nStep 10- The Consortium’s DIDComm Agent (C:1) identifies the goal code UUID and recognizes that it refers to the ongoing OEM enrollment and creates a new entry into the Agent Table. ")
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
        connection_value = "OEM_EGW"
        cursor.execute(insert_query, (connection_value,))
        connection.commit()

        cursor.close()

    except psycopg2.Error as e:
        print("Error:", e)
        print("error")

    finally:
        if connection:
            connection.close()
            #print("Connection closed.")

def step11():
    print("\nStep 11- D:1 establishes a connection with O:1 using an implicit invitation which is known to Dave because he has access to the O:1")
    # get OEM EGW Public did
    url = 'http://0.0.0.0:8061/wallet/did/public'
    headers = { 'accept': 'application/json' }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        pub_did = response_data["result"]["did"]
    else:
        print("error")
        return response.status_code
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
    #Implicit invitation from dave to oem egw
    url = 'http://0.0.0.0:8201/didexchange/create-request'
    params = { 'their_public_did': pub_did, 'alias': "oem_egw", 'my_label': "dave" }
    headers = { 'accept': 'application/json' }

    response = requests.post(url, params=params, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        return response_data
    else:
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
        return response.status_code



def main():
    execution_times = []
    cpu_usage = []
    ram_usage = []

    r, t = tfv2.time_execution(step1)
    execution_times.append(t)
    cpu_percent, ram_percent = tfv2.get_resource_usage()
    cpu_usage.append(cpu_percent)
    ram_usage.append(ram_percent)
    r, t = tfv2.time_execution(step2)
    execution_times.append(t)
    cpu_percent, ram_percent = tfv2.get_resource_usage()
    cpu_usage.append(cpu_percent)
    ram_usage.append(ram_percent)    
    r, t = tfv2.time_execution(step3)
    execution_times.append(t)
    cpu_percent, ram_percent = tfv2.get_resource_usage()
    cpu_usage.append(cpu_percent)
    ram_usage.append(ram_percent)
    r4, t = tfv2.time_execution(step4)
    execution_times.append(t)
    cpu_percent, ram_percent = tfv2.get_resource_usage()
    cpu_usage.append(cpu_percent)
    ram_usage.append(ram_percent)
    r, t = tfv2.time_execution(step5)
    execution_times.append(t)
    cpu_percent, ram_percent = tfv2.get_resource_usage()
    cpu_usage.append(cpu_percent)
    ram_usage.append(ram_percent)
    r, t = tfv2.time_execution(step6)
    execution_times.append(t)
    cpu_percent, ram_percent = tfv2.get_resource_usage()
    cpu_usage.append(cpu_percent)
    ram_usage.append(ram_percent)
    time.sleep(10)
    r, t = tfv2.time_execution(step7)
    execution_times.append(t)
    cpu_percent, ram_percent = tfv2.get_resource_usage()
    cpu_usage.append(cpu_percent)
    ram_usage.append(ram_percent)
    r, t = tfv2.time_execution(step8)
    execution_times.append(t)
    cpu_percent, ram_percent = tfv2.get_resource_usage()
    cpu_usage.append(cpu_percent)
    ram_usage.append(ram_percent)
    print(r4)
    r, t = tfv2.time_execution(step9, r4)
    execution_times.append(t)
    cpu_percent, ram_percent = tfv2.get_resource_usage()
    cpu_usage.append(cpu_percent)
    ram_usage.append(ram_percent)
    r, t = tfv2.time_execution(step10)
    execution_times.append(t)
    cpu_percent, ram_percent = tfv2.get_resource_usage()
    cpu_usage.append(cpu_percent)
    ram_usage.append(ram_percent)
    r11, t = tfv2.time_execution(step11)
    
    #n(step11)
    execution_times.append(t)
    cpu_percent, ram_percent = tfv2.get_resource_usage()
    cpu_usage.append(cpu_percent)
    ram_usage.append(ram_percent)
    print(r11)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot Gantt chart (bar plot) on the same subplot
    ax.barh(range(len(execution_times)), execution_times, color='blue')
    ax.set_yticks(range(len(execution_times)))
    ax.set_yticklabels(["Step {}".format(i+1) for i in range(len(execution_times))])
    ax.set_xlabel('Execution Time')
    ax.set_ylabel('Steps')
    ax.set_title('Execution Time Gantt Chart')

    # Plot CPU and RAM usage (line plots) on the same subplot
    ax.plot(cpu_usage, label='CPU Usage')
    ax.plot(ram_usage, label='RAM Usage')
    ax.set_xlabel('Steps')
    ax.set_ylabel('Usage (%)')
    ax.set_title('Resource Usage Over Steps')
    ax.legend()

    # Show the combined plot
    plt.show()

    #return r11



"""def main():
    execution_times = []
    cpu_usage = []
    ram_usage = []

    for step in [step1, step2, step3, step4, step5, step6, step7, step8, step9, step10, step11]:
        response, exe_time = tfv2.time_execution(step)

        execution_times.append(exe_time)
        cpu_percent, ram_percent = tfv2.get_resource_usage()
        cpu_usage.append(cpu_percent)
        ram_usage.append(ram_percent)

    # Create Gantt chart
    plt.figure(figsize=(10, 6))
    plt.barh(range(len(execution_times)), execution_times, color='blue')
    plt.yticks(range(len(execution_times)), ["Step {}".format(i+1) for i in range(len(execution_times))])
    plt.xlabel('Execution Time')
    plt.ylabel('Steps')
    plt.title('Execution Time Gantt Chart')
    plt.tight_layout()

    # Plot CPU and RAM usage
    plt.figure(figsize=(10, 6))
    plt.plot(cpu_usage, label='CPU Usage')
    plt.plot(ram_usage, label='RAM Usage')
    plt.xlabel('Steps')
    plt.ylabel('Usage (%)')
    plt.title('Resource Usage Over Steps')
    plt.legend()
    plt.tight_layout()

    plt.show()

    return response"""


if __name__ == "__main__":
    main()