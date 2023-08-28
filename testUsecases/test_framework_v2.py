import subprocess, os
from pathlib import Path
import docker
import time
import AgentsDeployment.deploy_agents as agents

import UseCases.uc1_oem_enroll_1 as uc1
import UseCases.uc2_oem_enroll_2 as uc2
import UseCases.uc3_dev_model_reg as uc3
import UseCases.uc4_dev_self_reg as uc4
import UseCases.uc5_consumer_buys_dev as uc5
import UseCases.uc6_dev_claim as uc6
import UseCases.uc7_dev_twin as uc7
import UseCases.uc8_dev_untwin as uc8
#import UseCases.run_all_uc as run_all
import psutil
import requests
import base64


def remove_containers(container_names=None):
    docker_stop_cmd="docker stop"
    docker_rm_cmd="docker rm"
    if container_names == None:
        docker_stop_cmd = "docker stop $(docker ps -aq)"
        docker_rm_cmd = "docker rm $(docker ps -aq)"
    else:
        for container_name in container_names:
            docker_stop_cmd += f" {container_name}"
            docker_rm_cmd += f" {container_name}"

    try:
        subprocess.run(docker_stop_cmd + " && " + docker_rm_cmd, shell=True, check=True)
        print("All containers stopped successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error while executing Docker command: {e}")

def change_to_root_dir():
    current_dir = os.getcwd()
    while current_dir != '/':
        if '.git' in os.listdir(current_dir):
            os.chdir(current_dir)
            return
        current_dir = os.path.dirname(current_dir)

def are_containers_deployed(container_names):
    try:
        client = docker.from_env()
        for container_name in container_names:
            try:
                container = client.containers.get(container_name)
                return True
            except docker.errors.NotFound:
                return False
    except docker.errors.APIError as e:
        print(f"Error connecting to the Docker daemon: {e}")

def time_execution(func, *args, **kwargs):
    """
    Measures the time taken by a function to execute.

    Parameters:
        func (function): The target function to be executed.
        *args: Positional arguments to be passed to the function.
        **kwargs: Keyword arguments to be passed to the function.

    Returns:
        tuple: A tuple containing the result of the function and the time taken to execute it (in seconds).
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    elapsed_time = end_time - start_time
    #if(result != None):
        #print("Result:", result)
    print("Time taken: {:.3f} seconds".format(elapsed_time))
    return result, elapsed_time


def get_resource_usage():
    cpu_percent = psutil.cpu_percent(interval=0.1)
    ram_percent = psutil.virtual_memory().percent
    return cpu_percent, ram_percent

def deploy_fabric_network():
    containers = ["peer0.org1.example.com"]
    if not are_containers_deployed(containers):
        change_to_root_dir()
        print("Deploying Fabric Network")
        os.chdir("Masters-v2/Fabric/fabric-network-cc/")
        command = 'python3 deploy_fabric.py'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Fabric Network deployed")

def deploy_ipfs_node():
    containers = ["ipfs"]
    if not are_containers_deployed(containers):
        change_to_root_dir()
        print("Deploying IPFS Node")
        os.chdir("Masters-v2/IPFS/")
        command = 'docker run -it -d \
                    --name ipfs \
                    --network docker_default \
                    -p 4001:4001 \
                    -p 5002:5002 \
                    -p 8070:8070 \
                    yeasy/ipfs'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("IPFS Node deployed")

def deploy_gateway():
    containers = ["ditto-ipfs-fabric"]
    if not are_containers_deployed(containers):
        change_to_root_dir()
        print("Deploying Gateway")
        os.chdir("Masters-v2/Gateway/")
        command = 'python3 initGateway.py'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Gateway deployed")

def deploy_smartdevice():
    containers = ["iwatch-container"]
    if not are_containers_deployed(containers):
        change_to_root_dir()
        print("Deploying Smart Device")
        os.chdir("Masters-v2/SmartDevice/")
        command = 'python3 initSD.py'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Smart Device deployed")    

def deploy_aries_agents():
    #DEPLOY CONSORTIUM AGENT
    result, elapsed_time = time_execution(agents.deploy_consortium)

    #DEPLOY OEM EGW AGENT
    #deployed in uc1_6
    #result, elapsed_time = time_execution(agents.deploy_oem_egw)

    #DEPLOY OEM SD AGENT
    result, elapsed_time = time_execution(agents.deploy_oem_sd)

    #DEPLOY DAVE AGENT
    result, elapsed_time = time_execution(agents.deploy_dave)

    #DEPLOY EGW AGENT
    #deployed in uc4_1_2
    #result, elapsed_time = time_execution(agents.deploy_egw)

    #DEPLOY SD AGENT
    #deployed in uc4_2_2
    #result, elapsed_time = time_execution(agents.deploy_sd)

    #DEPLOY ALICE AGENT
    result, elapsed_time = time_execution(agents.deploy_alice)

    #DEPLOY BOB AGENT
    result, elapsed_time = time_execution(agents.deploy_bob)

    #DEPLOY CHARLIE AGENT
    result, elapsed_time = time_execution(agents.deploy_charlie)

    print("Aries Agents Deployed")


def get_cpu_ram_usage(interval=0.1, cpu_usage=[], ram_usage=[], stop_event=None):
    while not stop_event.is_set():
        cpu_percent = psutil.cpu_percent(interval=interval)
        ram_percent = psutil.virtual_memory().percent

        cpu_usage.append(cpu_percent)
        ram_usage.append(ram_percent)

def run_use_cases():
    #DONE
    print("\n ==========================UC1========================== \n")
    uc1.main()
    time.sleep(15)

    #DONE
    print("\n ==========================UC2========================== \n")
    uc2.main()
    time.sleep(15)

    #DONE
    print("\n ==========================UC3========================== \n")
    uc3.main()
    time.sleep(15)

    #DONE
    print("\n ==========================UC4========================== \n")
    uc4.main()
    time.sleep(15)
    
    #DONE
    print("\n ==========================UC5========================== \n")
    uc5.main()
    time.sleep(15)

    print("\n ==========================UC6========================== \n")
    uc6.main()
    time.sleep(15)

    print("\n ==========================UC7========================== \n")
    uc7.main()
    time.sleep(15)

    print("\n ==========================UC8========================== \n")
    uc8.main()


def save_on_git_hub(plot_name):
    print(plot_name)
    access_token = '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'

    # Set the repository details
    owner = 'paquino11'
    repo = 'plots'

    # Set the branch where you want to add the file
    branch = 'main'  # Replace with the desired branch name

    # Set the file details
    change_to_root_dir()
    os.chdir("testUsecases/")
    file_path1 = plot_name
    # Read the content of the file
    with open(file_path1, 'rb') as file:        
        file_content = file.read()

    # Set the API endpoint URL
    import datetime

    current_timestamp = str(datetime.datetime.now())

    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{plot_name}'

    # Set the headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Prepare the request payload
    data = {
        'message': 'Add file via API',
        'content': base64.b64encode(file_content).decode()
    }

    # Encode the file content as base64

    #data['content'] = base64.b64encode(data['content'].encode()).decode()

    # Send the POST request to create the file
    response = requests.put(url, headers=headers, json=data)

    # Check the response
    if response.status_code == 201:
        print('File added successfully!')
    else:
        print(f'Failed to add file. Status code: {response.status_code}, Error message: {response.json()["message"]}')






def main():
    #REMOVE ALL DOCKER CONTAINERS
    #remove_containers()

    #DEPLOY FABRIC NETWORK
    result, elapsed_time = time_execution(deploy_fabric_network)
  
    #DEPLOY IPFS Node
    result, elapsed_time = time_execution(deploy_ipfs_node)

    #DEPLOY GATEWAY
    #deployed in uc7_6
    #result, elapsed_time = time_execution(deploy_gateway)

    #DEPLOY SMART DEVICE
    #deployed in uc7_8
    #result, elapsed_time = time_execution(deploy_smartdevice)

    #containers_to_remove = ["consortium", "consortium-postgres", "oem_egw", "oem_sd", "dave", "gatewayv2", "gateway-postgres", "smartdevice", "alice", "bob", "charlie"]
    #remove_containers(containers_to_remove)

    #DEPLOY ARIES AGENTS
    result, elapsed_time = time_execution(deploy_aries_agents)
    #result, elapsed_time = time_execution(agents.deploy_consortium)

    #RUN USE CASES
    run_use_cases()


if __name__ == "__main__":
    main()

