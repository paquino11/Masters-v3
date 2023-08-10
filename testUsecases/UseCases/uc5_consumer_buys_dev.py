import sys
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')  # Add the path to the directory containing test.py
import test_framework_v2 as tfv2



def step1():
    print("Step 1- Alice searches the Marketplace App  ")

def step2():
    print("Step 2- Alice taps the “buy” button that is associated with the OEM’s OOB URI and the goal c2dt.consortium.buydevice which open’s Alice’s mobile wallet (for simplification we are omitting Alice’s mediator agent).  ")

def step3():
    print("Step 3- A:1 send the OOB URI to O:1.  ")

def step4():
    print("Step 4- O:1 recognizes the A:1 wants to buy device and proposes the Ownership VC along with the price. ")

def step5():
    print("Step 5- Alice accepts the VC offer and initiates the payment subprocess which will transfer the necessary funds from Alice to the OEM (out-of-scope). ")

def step6():
    print("Step 6- Upon confirming the funds, O:1 makes an update to the DT ledger indicating that the device is “In-Transit”.  ")






def main():
    tfv2.time_execution(step1)
    tfv2.time_execution(step2)
    tfv2.time_execution(step3)
    tfv2.time_execution(step4)
    tfv2.time_execution(step5)
    tfv2.time_execution(step6)


if __name__ == "__main__":
    main()