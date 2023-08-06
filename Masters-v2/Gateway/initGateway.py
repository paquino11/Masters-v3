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

subprocess.call("pip3 install -r requirements.txt", shell=True)

# Run app.py
subprocess.call("python3 app.py", shell=True)


