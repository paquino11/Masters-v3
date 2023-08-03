TO CREATE A DT 
cd Automate-Twin-Process 
python3 twin_sd.py 
Please enter your Device ID: iwatch 
Please enter your Device Definition: https://raw.githubusercontent.com/bernar0507/Eclipse-Ditto-MQTT-iWatch/main/iwatch/wot/iwatch.tm.jsonld 

TO SIMULATE SENDING DATA FROM SMART DEVICE 
cd Eclipse-Ditto-MQTT-iWatch/iwatch/dockerfile 
docker build --no-cache  -t iwatch_image -f Dockerfile.iwatch . 
docker run -it --name iwatch-container --network docker_default iwatch_image