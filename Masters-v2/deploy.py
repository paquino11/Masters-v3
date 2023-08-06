import os, subprocess
import docker


def are_containers_deployed(container_names):
    try:
        client = docker.from_env()

        for container_name in container_names:
            try:
                container = client.containers.get(container_name)
                print(f"Container '{container_name}' is already deployed.")
                return True
            except docker.errors.NotFound:
                print(f"Container '{container_name}' is not deployed.")
                return False

    except docker.errors.APIError as e:
        print(f"Error connecting to the Docker daemon: {e}")


#DEPLOY FABRIC
os.chdir("Fabric/fabric-network-cc/")
containers_to_check = ["ca_orderer", "ca_org1", "ca_org2", "couchdb1", "orderer.example.com", 
                       "couchdb0", "peer0.org2.example.com", "peer0.org1.example.com"
                       , "cli", "fabric-gateway"]
if not are_containers_deployed(containers_to_check):
        command = 'python3 deploy_fabric.py'
        process = subprocess.call(command, shell=True)

#DEPLOY IPFS
containers_to_check = ["ipfs"]
os.chdir("../../IPFS")
if not are_containers_deployed(containers_to_check):
        command = 'docker run -it -d \
                --name ipfs \
                --network docker_default \
                -p 4001:4001 \
                -p 5002:5002 \
                -p 8070:8070 \
                yeasy/ipfs'
        process = subprocess.call(command, shell=True)
#command = 'docker run -d -p 5001:5001 --name ditto-ipfs --network docker_default ditto-ipfs-image'
#process = subprocess.call(command, shell=True)

#DEPLOY GATEWAY
os.chdir("../Gateway/")
command = 'python3 initGateway.py'
process = subprocess.call(command, shell=True)

#DEPLOY SMART DEVICE
os.chdir("../SmartDevice/")
command = 'python3 initSD.py'
process = subprocess.call(command, shell=True)