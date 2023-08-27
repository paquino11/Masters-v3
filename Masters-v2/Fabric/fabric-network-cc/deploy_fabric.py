import subprocess
import os
import time


os.chdir("fabric-samples/test-network/")

subprocess.call("./network.sh down -c dtnetwork", shell=True)

subprocess.call("./network.sh up createChannel -c dtnetwork -ca -s couchdb", shell=True)

subprocess.call("./network.sh deployCC -c dtnetwork -ccn chaincode1 -ccp ../../chaincode1 -ccl go", shell=True)

os.chdir("../")

subprocess.call("docker build -t fabric-gateway .", shell=True)

subprocess.call("docker run -d -p 3025:3025 --name fabric-gateway --network docker_default fabric-gateway", shell=True)
