import sys
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')
import test_framework_v2 as tfv2


def step1():
    print("Step 1- B:1 request action menu from egw:1 ")

def step2():
    print("Step 2- B:1 selects the “Twin” “Action Menu” and submits the following information: \
                SD_UUID - created by the SD during the 1st boot. \
                Untwin configurations - While this is not part of this study, at this point Bob could in the future define untwining configurations such as whether he wants to delete all the data, part of the data, or to maintain all data.")

def step3():
    print("Step 3- egw:1 sends a message to sd:1 to stop streaming data.  ")

def step4():
    print("Step 4- egw:1 update the Device Table and removes the asset being untwined.  ")

def step5():
    print("Step 5- egw:1 deletes the twin. ")

def step6():
    print("Step 6- egw:1 based on the untwin configurations may or not remove data from IPFS. ")

def step7():
    print("Step 7- egw:1updates the DTE ledger. This is important from a trustworthiness of the data because no data sets can be associated to this asset from this point onwards. ")




def main():
    tfv2.time_execution(step1)
    tfv2.time_execution(step2)
    tfv2.time_execution(step3)
    tfv2.time_execution(step4)
    tfv2.time_execution(step5)
    tfv2.time_execution(step6)
    tfv2.time_execution(step7)


if __name__ == "__main__":
    main()