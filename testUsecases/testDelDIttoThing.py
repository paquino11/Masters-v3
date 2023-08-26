import requests


device_id="iwatch"
#definition = input("Please enter your Device Definition: ")
definition = "https://raw.githubusercontent.com/bernar0507/Eclipse-Ditto-MQTT-iWatch/main/iwatch/wot/iwatch.tm.jsonld "
url = f"http://localhost:8080/api/2/things/org.Iotp2c:{device_id}"
auth = ("ditto", "ditto")
response = requests.delete(url, auth=auth)
if response.status_code == 200:
    print("DT already created")
else:
    print(response.text)