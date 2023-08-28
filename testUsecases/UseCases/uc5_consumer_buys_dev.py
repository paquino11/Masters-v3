import sys, requests, time, json, threading, datetime
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')
import test_framework_v2 as tfv2
import matplotlib.pyplot as plt
import numpy as np
import psutil

def step1():
    print("Step 1- Alice searches the Marketplace App  ")

def step2():
    print("Step 2- Alice taps the “buy” button that is associated with the OEM’s OOB URI and the goal c2dt.consortium.buydevice which open’s Alice’s mobile wallet (for simplification we are omitting Alice’s mediator agent).  ")

def step3():
    print("Step 3- A:1 send the OOB URI to O:1.  ")
    url = 'http://0.0.0.0:8181/out-of-band/create-invitation'
    params = { 'auto_accept': 'true', 'multi_use': 'false' }

    headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' }

    data = { "handshake_protocols": [ "rfc23" ], "use_public_did": False, "goal_code": "c2dt.consortium.enroll.OEM?UUID" }

    response = requests.post(url, params=params, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        #print(response_data)#"""['invitation_url']"""
    else:
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
        #return response.text
        print("error")
    recipient_keys = response_data['invitation']['services'][0]['recipientKeys']
    invitation_id = response_data['invitation']['@id']
    service_endpoint = response_data['invitation']['services'][0]['serviceEndpoint']

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

def step4():
    print("Step 4- O:1 recognizes the A:1 wants to buy device and proposes the Ownership VC along with the price. ")
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
            #print("Enrollment VC ID:", enrollment_vc_id)
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
        #print("it was proposed")
        return connection_id
    else:
        #print(f"Request failed with status code: {response.status_code}")
        print("")

def step5():
    print("Step 5- Alice accepts the VC offer and initiates the payment subprocess which will transfer the necessary funds from Alice to the OEM (out-of-scope). ")
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
            #print("Enrollment VC ID:", enrollment_vc_id)
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
        #print("it was proposed")
        return connection_id
    else:
        #print(f"Request failed with status code: {response.status_code}")
        print("")

def step6():
    print("Step 6- Upon confirming the funds, O:1 makes an update to the DT ledger indicating that the device is “In-Transit”.  ")
    url = "http://localhost:3025/regdataset"
    payload = {"string": "EGWA AGent"}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Updated to in-transit")
    else:
        print("Failed to send string to the server.")






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
    r, t = tfv2.time_execution(step4)
    categories.append('4')
    values.append(t)
    r, t = tfv2.time_execution(step5)
    categories.append('5')
    values.append(t)
    r, t = tfv2.time_execution(step6)
    categories.append('6')
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
    print(cpu_usage)
    print(ram_usage)


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
    filename = f'UseCases/plots/uc1_1_{current_datetime}.png'

    # Save the plot to the constructed filename
    plt.savefig(filename)
    tfv2.save_on_git_hub(filename)
    plt.show()
    #print(values)   

if __name__ == "__main__":
    main()