import sys
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')
import test_framework_v2 as tfv2



def step1():
    print("Step 1- D:1 request the menu actions from C:1 using Aries RFC 0509. ")

def step2():
    print("Step 2- D:1 selects “Register Device Model” along with the information requested by the associated form which includes Name, Description, Features array, Images array, and WoT file. ")

def step3():
    print("Step 3- C:1 generates a DeviceModelID and anchors the information into DT Ledger. ")

def step4():
    print("Step 4- C:1 loads the WoT file to the consortium source control. ")

def step5():
    print("Step 5- C:1 loads the images and feature information to the Marketplace App. ")

def step6():
    print("Step 6- C:1 uses Aries RFC 009523 to send the deviceModelID along with DeviceName to O:1. ")


def main():
    tfv2.time_execution(step1)
    tfv2.time_execution(step2)
    tfv2.time_execution(step3)
    tfv2.time_execution(step4)
    tfv2.time_execution(step5)
    tfv2.time_execution(step6)


if __name__ == "__main__":
    main()