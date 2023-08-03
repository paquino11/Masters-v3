import subprocess
import os
import time

# Change directory
os.chdir("dittomqtt/Eclipse-Ditto-MQTT-iWatch/iwatch/dockerfile")

# Execute twin_sd.py
subprocess.call("docker build --no-cache  -t iwatch_image -f Dockerfile.iwatch .", shell=True)

subprocess.call("docker run -it --name iwatch-container --network docker_default iwatch_image", shell=True)
