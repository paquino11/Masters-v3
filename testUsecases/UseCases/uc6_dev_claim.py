import sys
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/') 
import test_framework_v2 as tfv2



def step1_1():
    print("Step 1- A:1 scans the EGW’s OOB QR code which has associated the goal code c2dt.consortium.claim. ")

def step2_1():
    print("Step 2- A:1 establishes a connection with egw:1.   ")

def step3_1():
    print("Step 3- egw:1 requests A:1 “EGW Ownership VC” proof.  ")

def step4_1():
    print("Step 4- A:1 submits proof which includes the EGW’s public DID and compares it with its own “Genesis VC”. ")

def step5_1():
    print("Step 5- egw:1 updates the device status on the DT Ledger setting the EGW state to “CLAIMED”. The controllerId is set to the did:peer Alice uses in the communication with EGW. This establishes the control relation between Alice and the EGW without compromising Alice’s privacy. ")


def step1_2():
    print("Step 1- B:1 requests the menu actions from egw:1. ")

def step2_2():
    print("Step 2- B:1 selects “Claim Smart Device”. ")

def step3_2():
    print("Step 3- egw:1 requests SD Ownership VC proof. ")

def step4_2():
    print("Step 4- A:1 sends presentation with Device ID. ")

def step5_2():
    print("Step 5- egw:1 initiates a transaction which associates the Device ID to the “claim device” action. ")

def step6_2():
    print("Step 6- B:1 scans the SD QR code which has associated the goal c2dt.consortium.claim. ")

def step7_2():
    print("Step 7- B:1 scans the SD QR code which has associated the goal c2dt.consortium.claim. ")

def step8_2():
    print("Step 8- Based on the goal code sd:1 requests EGW’s standing invitation. ")

def step9_2():
    print("Step 9- B:1 sends EGW standing invitation. ")

def step10_2():
    print("Step 10- B:1 uses the standing invitation to establish an implicit invitation to egw:1 passing the goal code c2dt.consortium.claim.  ")

def step11_2():
    print("Step 11- egw:1 requests SD Genesis VC proof. ")

def step12_2():
    print("Step 12- B:1 submit presentation that includes device ID. ")

def step13_2():
    print("Step 13- egw:1 sends a confirmation request to A:1 to ensure that Alice approves Bob’s SD association with EGW. ")

def step14_2():
    print("Step 14- egw:1 completes the transaction and associates the B:1 DID peer to the device ID. From this point onwards egw:1 knows which consumer owns what device. ")

def step15_2():
    print("Step 15- egw:1 updates the DT ledger and updates the controller ID to the EGW public DID, and the state to “claimed”. ")




def main():
    print("EGW CLAIM")
    tfv2.time_execution(step1_1)
    tfv2.time_execution(step2_1)
    tfv2.time_execution(step3_1)
    tfv2.time_execution(step4_1)
    tfv2.time_execution(step5_1)
    print("SD CLAIM")
    tfv2.time_execution(step1_2)
    tfv2.time_execution(step2_2)
    tfv2.time_execution(step3_2)
    tfv2.time_execution(step4_2)
    tfv2.time_execution(step5_2)
    tfv2.time_execution(step6_2)
    tfv2.time_execution(step7_2)
    tfv2.time_execution(step8_2)
    tfv2.time_execution(step9_2)
    tfv2.time_execution(step10_2)
    tfv2.time_execution(step11_2)
    tfv2.time_execution(step12_2)
    tfv2.time_execution(step13_2)
    tfv2.time_execution(step14_2)
    tfv2.time_execution(step15_2)

if __name__ == "__main__":
    main()