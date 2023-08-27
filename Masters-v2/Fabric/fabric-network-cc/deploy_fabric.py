import subprocess
import os
import time


os.chdir("fabric-samples/test-network/")

subprocess.call("./network.sh down -c dtnetwork1", shell=True)

subprocess.call("./network.sh up createChannel -c dtnetwork1 -ca -s couchdb", shell=True)

subprocess.call("./network.sh deployCC -c dtnetwork1 -ccn chaincode1 -ccp ../../chaincode1 -ccl go", shell=True)

current_directory = os.getcwd()
print("Current Directory:", current_directory)
os.chdir("../")

subprocess.call("docker build -t fabric-gateway .", shell=True)

subprocess.call("docker run -d -p 3025:3025 --name fabric-gateway --network docker_default fabric-gateway", shell=True)
