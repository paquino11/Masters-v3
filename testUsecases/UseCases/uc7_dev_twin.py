import sys, requests, threading, datetime, time
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')
import test_framework_v2 as tfv2
import psycopg2, os
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import test_framework_v2 as tfv2
import matplotlib.pyplot as plt
import numpy as np
import psutil

def step1():
    print("Step 1- B:1 request action menu from egw:1 ")
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
    print("Step 2-  B:1 selects the “Twin” “Action Menu” and submits the following information: \
          SD_UUID - created by the SD during the 1st boot. \
          twining configuration – currently defines solely frequency with which files are written to decentralized storage (e.g., 24h). ")
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
            #print(f"Connection ID for 'oem.egw.agent': {connection_id}")
            print("")
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
def step3():
    print("Step 3- egw:1 requests approval from A:1 to twin the device. ")

def step4():
    print("Step 4- egw:1 uploads the twinning configurations to the SD Table. ")
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

def step5():
    print("Step 5- egw:1 downloads the WoT file from the Consortium Git by querying the corresponding DeviceModelID from the SD Table (which is stored during the “SD claim”).  ")
    import requests
    import base64

    access_token = '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'

    # Set the repository details
    owner = 'paquino11'
    repo = 'wot_files'

    # Set the branch and file path you want to download
    branch = 'main'  # Replace with the desired branch name
    file_path = 'wotfile1.txt'  # Replace with the desired file path

    # Set the API endpoint URL
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}'

    # Set the headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Send the GET request to retrieve the file content
    response = requests.get(url, headers=headers)

    # Check the response
    if response.status_code == 200:
        # Decode the base64 content
        file_content_base64 = response.json()['content']
        file_content_bytes = base64.b64decode(file_content_base64)
        file_content = file_content_bytes.decode('utf-8')
        
        # Print or save the downloaded content
        print(file_content)
    else:
        print(f'Failed to download file. Status code: {response.status_code}, Error message: {response.json()["message"]}')

def step6():
    print("Step 6- egw:1 starts DT server and deploys the SD DT using the WoT file. ")
 #init gateway
    result, elapsed_time = tfv2.time_execution(tfv2.deploy_gateway)

def step7():
    print("Step 7- egw:1 sends a message to sd:1 to start streaming data which includes the MQTT topic. ")
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

    base_url = 'http://localhost:8081/connections/'

    url = f'{base_url}{connection_id}/send-message'

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    data = {
        "content": "start streaming data"
    }

    response = requests.post(url, headers=headers, json=data)

def step8():
    print("Step 8- sd:1 needs to configure the MQTT Client.  ")
    result, elapsed_time = tfv2.time_execution(tfv2.deploy_smartdevice)


def step9():
    print("Step 9- egw:1 updates the state of the SD to “Twined”. ")
    url = "http://localhost:3025/regdataset"
    payload = {"string": "twinned"}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("iWatch Twinned")
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
    r, t = tfv2.time_execution(step7)
    categories.append('7')
    values.append(t)
    r, t = tfv2.time_execution(step8)
    categories.append('8')
    values.append(t)
    r, t = tfv2.time_execution(step9)
    categories.append('9')
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

    bar_starts = np.roll(cumulative_values, 1)
    bar_starts[0] = 0  # Set the left value of the first bar to 0
    bar_durations = non_zero_values
    bar_midpoints = np.array([bar_start + duration / 2 for bar_start, duration in zip(bar_starts, bar_durations)])
    bars = ax.barh(non_zero_categories, bar_durations, left=bar_starts, alpha=0.6)
    # Add values to the middle of each bar
    for i, (category, midpoint) in enumerate(zip(non_zero_categories, bar_midpoints)):
        value = bar_durations[i]
        ax.text(midpoint+7, i, f'{value:.3f} s', va='center', ha='center')

    ax.set_xlabel('Time')
    ax.set_ylabel('Steps')
    ax.set_xlim(0, sum(non_zero_values))


    """something = False
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
                cpu_usage.pop()"""
    
    # Create a second subplot for the CPU usage
    #cpu_ax = ax.twinx()
    #cpu_ax.plot(time_values, cpu_usage, color='r', label='CPU usage')
    #cpu_ax.set_ylabel('CPU usage (%)')

    # Create a third subplot for the RAM usage
    """ram_ax = ax.twinx()
    ram_ax.plot(ram_usage, color='b', label='RAM usage')
    ram_ax.set_ylabel('RAM usage (GB)')

    # Adjust the position of the RAM usage subplot
    ram_ax.spines['right'].set_position(('outward', 60))
    ram_ax.set_ylim(0, max(ram_usage))
    ram_ax.yaxis.label.set_color('b')
    ram_ax.tick_params(axis='y', colors='b')

    # Add a legend
    fig.legend(loc='upper right')

    plt.tight_layout()  # Adjust the layout to prevent overlapping"""
        # Get the current date and time
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Construct the filename with the current date and time
    tfv2.change_to_root_dir()
    current_directory = os.getcwd()
    print("Current Directory:", current_directory)
    os.chdir('testUsecases/UseCases/plots/')
    current_directory = os.getcwd()
    print("Current Directory:", current_directory)
    filename = f'uc7_{current_datetime}.png'
    time.sleep(1)

    # Save the plot to the constructed filename
    plt.savefig(filename)
    time.sleep(1)
    tfv2.save_on_git_hub(filename)
    plt.show()
    #print(values)   

if __name__ == "__main__":
    main()