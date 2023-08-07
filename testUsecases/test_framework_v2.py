import subprocess, os
from pathlib import Path

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



def deploy_fabric_network():
    change_to_root_dir()
    print("Deploying Fabric Network")
    os.chdir("Masters-v2/Fabric/fabric-network-cc/")
    command = 'python3 deploy_fabric.py'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Fabric Network deployed")

def deploy_ipfs_node():
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
    change_to_root_dir()
    print("Deploying Gateway")
    os.chdir("Masters-v2/Gateway/")
    command = 'python3 initGateway.py'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Gateway deployed")

def deploy_smartdevice():
    change_to_root_dir()
    print("Deploying Smart Device")
    os.chdir("Masters-v2/SmartDevice/")
    command = 'python3 initSD.py'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Smart Device deployed")    



def main():
    #REMOVE ALL DOCKER CONTAINERS
    remove_docker_containers()

    #DEPLOY FABRIC NETWORK
    deploy_fabric_network()

    #DEPLOY IPFS Node
    deploy_ipfs_node()

    #DEPLOY GATEWAY
    #deploy_gateway()

    #DEPLOY SMART DEVICE
    #deploy_smartdevice()





if __name__ == "__main__":
    main()