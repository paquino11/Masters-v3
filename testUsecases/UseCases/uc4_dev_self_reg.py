import sys
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')  # Add the path to the directory containing test.py
import test_framework_v2 as tfv2



def step1_1():
    print("Step 1- The OEM integrates the consortium firmware libraries. ")

def step2_1():
    print("Step 2- During first boot, the EGW executes a script that boots egw:1.  ")

def step3_1():
    print("Step 3- egw:1 creates the public DID. ")

def step4_1():
    print("Step 4- egw:1 utilizes the configuration files with the OEM’s public DID and implicit connection invitation to O:1 using goal c2dt.consortium.registerdevice?DID. ")

def step5_1():
    print("Step 5- O:1 sends egw:1 the Genesis VC proposal using Aries RFC 045324. ")

def step6_1():
    print("Step 6- O:1 registers EGW into the DT ledger and creates the EGW’s DT Ledger client user credentials which are required because the EGW must be able to write to the ledger. ")

def step7_1():
    print("Step 7- O:1 makes the SD available for the sale in the Marketplace App by associating the “buy button” URL as the OEM’s OOB Link with the goal c2dt.consortium.buydevice, along with the sale information.  ")

def step8_1():
    print("Step 8- O:1 sends egw:1 the Genesis VC. ")


def step1_2():
    print("Step 1- The OEM integrates the consortium firmware libraries. ")

def step2_2():
    print("Step 2- During the first boot, the SD executes a script that boots sd:1. ")

def step3_2():
    print("Step 3- sd:1 generates an UUID. ")

def step4_2():
    print("Step 4- sd:1 utilizes the configuration files that were set by the OEM and sends an implicit invitation to O:1 to establish a connection with the goal c2dt.consortium.registerdevice?UUID. ")

def step5_2():
    print("Step 5- O:1 sends sd:1 the Genesis VC proposal. ")

def step6_2():
    print("Step 6- O:1 register devices into the DT ledger. ")

def step7_2():
    print("Step 7- O:1 makes the SD available for the sale in the Marketplace App by associating the “buy button” URL as the OEM’s OOB Link with the goal c2dt.consortium.buydevice, along with the sale information. ")

def step8_2():
    print("Step 8- O:1 sends sd:1 the Genesis VC. ")





def main():
    print("EGW SELF REG")
    tfv2.time_execution(step1_1)
    tfv2.time_execution(step2_1)
    tfv2.time_execution(step3_1)
    tfv2.time_execution(step4_1)
    tfv2.time_execution(step5_1)
    tfv2.time_execution(step6_1)
    tfv2.time_execution(step7_1)
    tfv2.time_execution(step8_1)

    print("sd SELF REG")
    tfv2.time_execution(step1_2)
    tfv2.time_execution(step2_2)
    tfv2.time_execution(step3_2)
    tfv2.time_execution(step4_2)
    tfv2.time_execution(step5_2)
    tfv2.time_execution(step6_2)
    tfv2.time_execution(step7_2)
    tfv2.time_execution(step8_2)

if __name__ == "__main__":
    main()