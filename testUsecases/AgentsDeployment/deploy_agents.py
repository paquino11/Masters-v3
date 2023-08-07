import subprocess, os
import test_framework_v2 as test

def deploy_consortium():
    containers = ["consortium"]
    if not test.are_containers_deployed(containers):
        test.change_to_root_dir()
        print("Deploying Consortium Agent")
        os.chdir("Agents/")
        command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run consortium'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Consortium Agent deployed")


def deploy_oem_egw():
    containers = ["oem_egw"]
    if not test.are_containers_deployed(containers):
        test.change_to_root_dir()
        print("Deploying OEM EGW Agent")
        os.chdir("Agents/")
        command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run oem_egw'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("OEM EGW Agent deployed")

def deploy_oem_sd():
    containers = ["oem_sd"]
    if not test.are_containers_deployed(containers):
        test.change_to_root_dir()
        print("Deploying OEM SD Agent")
        os.chdir("Agents/")
        command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run oem_sd'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("OEM SD Agent deployed")

def deploy_dave():
    containers = ["dave"]
    if not test.are_containers_deployed(containers):
        test.change_to_root_dir()
        print("Deploying Dave Agent")
        os.chdir("Agents/")
        command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run dave'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Dave Agent deployed")

def deploy_egw():
    containers = ["gatewayv2"]
    if not test.are_containers_deployed(containers):
        test.change_to_root_dir()
        print("Deploying Edge Gateway Agent")
        os.chdir("Agents/")
        command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run gatewayv2'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Edge Gateway Agent deployed")

def deploy_sd():
    containers = ["smartdevice"]
    if not test.are_containers_deployed(containers):
        test.change_to_root_dir()
        print("Deploying Smart Device Agent")
        os.chdir("Agents/")
        command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run smartdevice'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Smart Device Agent deployed")

def deploy_alice():
    containers = ["alice"]
    if not test.are_containers_deployed(containers):
        test.change_to_root_dir()
        print("Deploying Alice Agent")
        os.chdir("Agents/")
        command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run alice'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Alice Agent deployed")

def deploy_bob():
    containers = ["bob"]
    if not test.are_containers_deployed(containers):
        test.change_to_root_dir()
        print("Deploying Bob Agent")
        os.chdir("Agents/")
        command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run bob'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Bob Agent deployed")

def deploy_charlie():
    containers = ["charlie"]
    if not test.are_containers_deployed(containers):
        test.change_to_root_dir()
        print("Deploying Charlie Agent")
        os.chdir("Agents/")
        command = 'LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run charlie'
        process = subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Charlie Agent deployed")