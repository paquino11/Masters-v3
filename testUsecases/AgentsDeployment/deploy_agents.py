import subprocess, os
import test_framework_v2

def deploy_consortium():
    test_framework_v2.change_to_root_dir()
    print("Deploying Consortium Agent")
    os.chdir("Agents/")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run consortium'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Fabric Network deployed")