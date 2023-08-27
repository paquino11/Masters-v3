# Steps:

## Deploy local IPFS Cluster

Inititate IPFS Ubuntu Application

## Deploy Fabric
```
cd Fabric/fabric-network-cc
python3 deploy_fabric.py 
```

## Deploy fabric app gateway
cd /home/pedro/Desktop/Aries-Agents/Masters-v2/Fabric/fabric-network-cc/fabric-samples
docker build -t fabric-gateway .
docker run -d -p 3025:3025 --name fabric-gateway --network docker_default fabric-gateway



### Query Batchs:
```
cd fabric-network-cc/fabric-samples/test-network
export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=$PWD/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051

peer chaincode query -C dtnetwork1 -n chaincode1 -c '{"Args":["GetAllDataBatchs"]}' | jq

cd fabric-network-cc/fabric-samples/test-network
export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=$PWD/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org2MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
export CORE_PEER_ADDRESS=localhost:9051

peer chaincode query -C dtnetwork1 -n chaincode1 -c '{"Args":["GetAllDataBatchs"]}' | jq
```

## Deploy Gateway
### Without Aries Agent
```
cd Gateway
python3 initGateway.py
```
### With Aries Agent (doesnt work yet)
```
cd aries-agent/demo/
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run gatewayv2
```
## Deploy Smart Device
### Without Aries Agent
```
cd SmartDevice
python3 initSD.py
```




