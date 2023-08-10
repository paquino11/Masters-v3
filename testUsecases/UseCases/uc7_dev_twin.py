import sys
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')  # Add the path to the directory containing test.py
import test_framework_v2 as tfv2



def step1():
    print("Step 1- B:1 request action menu from egw:1 ")

def step2():
    print("Step 2-  B:1 selects the “Twin” “Action Menu” and submits the following information: \
          SD_UUID - created by the SD during the 1st boot. \
          twining configuration – currently defines solely frequency with which files are written to decentralized storage (e.g., 24h). ")

def step3():
    print("Step 3- egw:1 requests approval from A:1 to twin the device. ")

def step4():
    print("Step 4- egw:1 uploads the twinning configurations to the SD Table. ")

def step5():
    print("Step 5- egw:1 downloads the WoT file from the Consortium Git by querying the corresponding DeviceModelID from the SD Table (which is stored during the “SD claim”).  ")

def step6():
    print("Step 6- egw:1 starts DT server and deploys the SD DT using the WoT file. ")

def step7():
    print("Step 7- egw:1 sends a message to sd:1 to start streaming data which includes the MQTT topic. ")

def step8():
    print("Step 8- sd:1 needs to configure the MQTT Client.  ")

def step9():
    print("Step 9- egw:1 updates the state of the SD to “Twined”. ")




def main():
    tfv2.time_execution(step1)
    tfv2.time_execution(step2)
    tfv2.time_execution(step3)
    tfv2.time_execution(step4)
    tfv2.time_execution(step5)
    tfv2.time_execution(step6)
    tfv2.time_execution(step7)
    tfv2.time_execution(step8)
    tfv2.time_execution(step9)

if __name__ == "__main__":
    main()