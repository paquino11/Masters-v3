import os,subprocess

def run_consortium():
    print('Deploying Consortium Agent')
    os.chdir("../../demo/")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run consortium'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_oem():
    print('Deploying OEM Agent')
    #os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run oemv2'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_dave():
    print('Deploying Dave Agent')
    #os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run dave'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_egw():
    print('Deploying Edge Gateway Agent')
    #os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run gatewayv2'
    #process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #os.chdir("/home/pedro/Desktop/Aries-Agents/Masters-v2/Gateway")
    #command = 'python3 initGateway.py'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_sd():
    print('Deploying Smart Device Agent')
    #os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run smartdevice'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_alice():
    print('Deploying Alice Agent')
    #os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run alice'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_bob():
    print('Deploying Bob Agent')
    #os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run bob'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_charlie():
    print('Deploying Charlie Agent')
    #os.chdir("/home/pedro/Desktop/Aries-Agents/demo")
    command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run charlie'
    process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    run_consortium()
    run_oem()
    run_dave()
    run_egw()
    run_sd()
    run_alice()
    run_bob()
    run_charlie()


if __name__ == "__main__":
    main()
