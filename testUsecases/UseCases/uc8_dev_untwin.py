import sys, requests, subprocess
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')
import test_framework_v2 as tfv2
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

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
            print(f"Consortium Connection ID: {consortium_connection_id}")
        else:
            print("No connection with alias 'consortium' found.")
    else:
        print(f"Request failed with status code: {response.status_code}")

    #request menu action
    url = f'http://localhost:8201/action-menu/{consortium_connection_id}/request'
    headers = {'accept': 'application/json'}

    response = requests.post(url, headers=headers, data='')

def step2():
    print("Step 2- B:1 selects the “Twin” “Action Menu” and submits the following information: \
                SD_UUID - created by the SD during the 1st boot. \
                Untwin configurations - While this is not part of this study, at this point Bob could in the future define untwining configurations such as whether he wants to delete all the data, part of the data, or to maintain all data.")

def step3():
    print("Step 3- egw:1 sends a message to sd:1 to stop streaming data.  ")
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

def step4():
    print("Step 4- egw:1 update the Device Table and removes the asset being untwined.  ")
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
    print("Step 5- egw:1 deletes the twin. ")
    input("Data is being send to Gateway. Press ENTER to untwin")
    container_name = "iwatch-container"
    try:
        subprocess.run(["docker", "stop", container_name], check=True)
        print(f"Container '{container_name}' successfully stopped.")
    except subprocess.CalledProcessError:
        print(f"Failed to stop container '{container_name}'.")

def step6():
    print("Step 6- egw:1 based on the untwin configurations may or not remove data from IPFS. ")

def step7():
    print("Step 7- egw:1 updates the DT ledger. This is important from a trustworthiness of the data because no data sets can be associated to this asset from this point onwards. ")
    url = "http://localhost:3025/regdataset"
    payload = {"string": "Controller ID updated"}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Updated Ledger")
    else:
        print("Failed to send string to the server.")



def main():
    tfv2.time_execution(step1)
    tfv2.time_execution(step2)
    tfv2.time_execution(step3)
    tfv2.time_execution(step4)
    tfv2.time_execution(step5)
    tfv2.time_execution(step6)
    tfv2.time_execution(step7)


if __name__ == "__main__":
    main()