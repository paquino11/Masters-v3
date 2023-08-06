import subprocess
import os
import time

# Change directory
os.chdir("dittomqtt/Automate-Twin-Process")

# Execute twin_sd.py
subprocess.call("python3 twin_sd.py", shell=True)

# Install dependencies
subprocess.call("ls")
os.chdir("../../ipfs-ditto/Eclipse-Ditto-IPFS")
"""
subprocess.call("pip3 install -r requirements.txt", shell=True)

# Run app.py
subprocess.call("python3 app.py", shell=True)

"""
subprocess.call("docker build -t ditto-ipfs-fabric .", shell=True)

# Run app.py
subprocess.call("docker run -d --name ditto-ipfs-fabric --network docker_default ditto-ipfs-fabric", shell=True)
