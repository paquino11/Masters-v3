import os, subprocess

current_path = os.getcwd()
print("Current Path:", current_path)


#DEPLOY IPFS
os.chdir("IPFS")
command = 'docker run -it -d \
        --name ipfs \
        -p 4001:4001 \
        -p 5002:5002 \
        -p 8080:8080 \
        yeasy/ipfs'
process = subprocess.call(command, shell=True)
#command = 'docker run -d -p 5001:5001 --name ditto-ipfs --network docker_default ditto-ipfs-image'
#process = subprocess.call(command, shell=True)

#DEPLOY FABRIC
os.chdir("../Fabric/fabric-network-cc/")
command = 'python3 deploy_fabric.py'
process = subprocess.call(command, shell=True)


#DEPLOY GATEWAY
os.chdir("../../Gateway/")
command = 'python3 initGateway.py'
process = subprocess.call(command, shell=True)