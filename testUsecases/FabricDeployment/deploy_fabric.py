import os, subprocess

def run_fabric():
    os.chdir("../../Masters-v2/Fabric/fabric-network-cc/")
    init_fabric_process = subprocess.call(['python3', 'deploy_fabric.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    run_fabric()


if __name__ == "__main__":
    main()
