import subprocess
import os
import time
import sys, threading
import requests
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/') 
import test_framework_v2 as tfv2
import AgentsDeployment.deploy_agents as agents
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import matplotlib.pyplot as plt
import numpy as np
import psutil, datetime


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
        #print(response_data)
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
        #print(response_data)
        return response_data
    else:
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
        return response.status_code



def main():

    categories = []
    values = []

    cpu_usage = []
    ram_usage = []
    stop_event = threading.Event()

    monitor_thread = threading.Thread(target=tfv2.get_cpu_ram_usage, args=(0.1, cpu_usage, ram_usage, stop_event))
    monitor_thread.start()

    r, t = tfv2.time_execution(step1)
    categories.append('1')
    values.append(t)
    r, t = tfv2.time_execution(step2)
    categories.append('2')
    values.append(t) 
    r, t = tfv2.time_execution(step3)
    categories.append('3')
    values.append(t)
    r4, t = tfv2.time_execution(step4)
    categories.append('4')
    values.append(t)
    r, t = tfv2.time_execution(step5)
    categories.append('5')
    values.append(t)
    r, t = tfv2.time_execution(step6)
    categories.append('6')
    values.append(t)
    time.sleep(10)
    r, t = tfv2.time_execution(step7)
    categories.append('7')
    values.append(t)
    r, t = tfv2.time_execution(step8)
    categories.append('8')
    values.append(t)
    #print(r4)
    r, t = tfv2.time_execution(step9, r4)
    categories.append('9')
    values.append(t)
    r, t = tfv2.time_execution(step10)
    categories.append('10')
    values.append(t)
    r11, t = tfv2.time_execution(step11)
    categories.append('11')
    values.append(t)

    #print(categories)
    #print(values)

    stop_event.set()

    monitor_thread.join()

    # Filter out categories and values with 0 values
    non_zero_categories = []
    non_zero_values = []
    for cat, val in zip(categories, values):
        if val != 0:
            non_zero_categories.append(cat)
            non_zero_values.append(val)


    # Calculate the cumulative sum of values
    cumulative_values = np.cumsum(non_zero_values)
    # Create a Gantt chart
    fig, ax = plt.subplots()

# Plot horizontal bars representing tasks
    bar_starts = np.roll(cumulative_values, 1)
    bar_durations = non_zero_values
    ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)
    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    ax.set_xlim(0, sum(non_zero_values))
    #print(cpu_usage)
    #print(ram_usage)


    something = False
    something1 = False
    while something == False:
        try:
            time_interval = 0.1  # Update interval in seconds
            num_points = len(cpu_usage) # Number of points to show on the graph
            time_values = np.arange(0, num_points * time_interval, time_interval)
            
            # Create a second subplot for the CPU usage
            cpu_ax = ax.twinx()
            cpu_ax.plot(time_values, cpu_usage, color='r', label='CPU usage (%)')
            cpu_ax.set_ylabel('CPU usage (%)')
            something = True
        except:
            print("error generating graph")
            if something1 == False:
                cpu_usage.append(psutil.cpu_percent())
            else:
                cpu_usage.pop()
                cpu_usage.pop()
    # Create a second subplot for the CPU usage
    #cpu_ax = ax.twinx()
    #cpu_ax.plot(time_values, cpu_usage, color='r', label='CPU usage')
    #cpu_ax.set_ylabel('CPU usage (%)')

    
    # Create a third subplot for the RAM usage
    ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping
    # Get the current date and time
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Construct the filename with the current date and time
    filename = f'UseCases/plots/uc1_{current_datetime}.png'

    # Save the plot to the constructed filename
    plt.savefig(filename)
    tfv2.save_on_git_hub(filename)
    plt.show()

    ##print(values)   

if __name__ == "__main__":
    main()