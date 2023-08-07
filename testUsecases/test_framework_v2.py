import subprocess, os
from pathlib import Path
import docker
import time
import AgentsDeployment.deploy_agents as agents


def remove_docker_containers():
    print("Removing all docker containers")
    try:
        containers = subprocess.check_output(['docker', 'ps', '-a', '-q']).decode().strip().split('\n')
        if not containers:
            return
        for container in containers:
            stop_command = "docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)"
            subprocess.run(stop_command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("")

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
    if(result != None):
        print("Result:", result)
    print("Time taken: {:.3f} seconds".format(elapsed_time))
    return result, elapsed_time


def deploy_fabric_network():
    containers = ["ca_orderer"]
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
    result, elapsed_time = time_execution(agents.deploy_oem_egw)

    #DEPLOY OEM SD AGENT
    result, elapsed_time = time_execution(agents.deploy_oem_sd)

    #DEPLOY DAVE AGENT
    result, elapsed_time = time_execution(agents.deploy_dave)

    #DEPLOY EGW AGENT
    result, elapsed_time = time_execution(agents.deploy_egw)

    #DEPLOY SD AGENT
    result, elapsed_time = time_execution(agents.deploy_sd)

    #DEPLOY ALICE AGENT
    result, elapsed_time = time_execution(agents.deploy_alice)

    #DEPLOY BOB AGENT
    result, elapsed_time = time_execution(agents.deploy_bob)

    #DEPLOY CHARLIE AGENT
    result, elapsed_time = time_execution(agents.deploy_charlie)

    print("Aries Agents Deployed")



def main():
    #REMOVE ALL DOCKER CONTAINERS
    #remove_docker_containers()

    #DEPLOY FABRIC NETWORK
    result, elapsed_time = time_execution(deploy_fabric_network)
  
    #DEPLOY IPFS Node
    result, elapsed_time = time_execution(deploy_ipfs_node)

    #DEPLOY GATEWAY
    result, elapsed_time = time_execution(deploy_gateway)

    #DEPLOY SMART DEVICE
    result, elapsed_time = time_execution(deploy_smartdevice)

    #DEPLOY ARIES AGENTS
    result, elapsed_time = time_execution(deploy_aries_agents)






if __name__ == "__main__":
    main()