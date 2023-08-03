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
subprocess.call("sudo apt-get install python3.11 python3-pip python3.11-dev python3.11-venv", shell=True)

# Create and activate virtual environment
#subprocess.call("python3.11 -m venv env", shell=True)
#subprocess.call("source env/bin/activate", shell=True)

# Install required packages

subprocess.call("pip3 install -r requirements.txt", shell=True)

# Run app.py
subprocess.call("python3 app.py", shell=True)


