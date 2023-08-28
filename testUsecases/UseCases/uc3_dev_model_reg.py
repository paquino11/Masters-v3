import sys, os, psutil, datetime
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')
import test_framework_v2 as tfv2
import requests, threading
import matplotlib.pyplot as plt
import numpy as np

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
            #print(f"Consortium Connection ID: {consortium_connection_id}")
            print("")
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
    url = "http://localhost:3025/regdataset"
    payload = {"string": "devmodel134"}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Dev Model registered!")
    else:
        print("Failed to send string to the server.")

def step4():
    print("Step 4- C:1 loads the WoT file to the consortium source control. ")
    access_token = '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'

    # Set the repository details
    owner = 'paquino11'
    repo = 'wot_files'

    # Set the branch where you want to add the file
    branch = 'main'  # Replace with the desired branch name

    # Set the file details
    tfv2.change_to_root_dir()
    os.chdir("testUsecases")
    file_path1 = 'wotfile.txt'
    # Read the content of the file
    with open(file_path1, 'r') as file:
        file_content = file.read()

    # Set the API endpoint URL
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


def step5():
    print("Step 5- C:1 loads the images and feature information to the Marketplace App. ")

def step6():
    print("Step 6- C:1 uses Aries RFC 0095 to send the deviceModelID along with DeviceName to O:1. ")
    #get oem connection of cons
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

    base_url = 'http://localhost:8181/connections/'

    url = f'{base_url}{connection_id}/send-message'

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    data = {
        "content": "Device Model ID: devmodel134, Device Name: iWatch"
    }

    response = requests.post(url, headers=headers, json=data)


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
            cpu_ax.plot(time_values, cpu_usage, color='r', label='CPU usage')
            cpu_ax.set_ylabel('CPU usage (%)')
            something = True
        except:
            print("error generating graph")
            if something1 == False:
                cpu_usage.append(psutil.cpu_percent())
            else:
                cpu_usage.pop()
                cpu_usage.pop()


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
    filename = f'UseCases/plots/uc3_{current_datetime}.png'

    # Save the plot to the constructed filename
    plt.savefig(filename)
    tfv2.save_on_git_hub(filename)
    plt.show()
    #print(values)   

if __name__ == "__main__":
    main()