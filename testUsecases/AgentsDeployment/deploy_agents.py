import subprocess, os

def deploy_consortium():
    print("Deploying COnsortium Agent")
    os.chdir("../Masters-v2/Fabric/fabric-network-cc/")
    command = 'python3 deploy_fabric.py'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Fabric Network deployed")