# Fabric Network Deployment

## This project has the objective of describing the necessary steps to deploy a fabric network with initial configurations, design, write and deploy chaincode, and add new organizations to our fabric network.

### Down existing Fabric Networks
```
cd /FabricNetwork/fabric-samples/test-network
./network.sh down -c dtnetwork1
```
### Up Network Fabric with couchdb
```
./network.sh up createChannel -c dtnetwork1 -ca -s couchdb
```
### Deploy chaincode
```
./network.sh deployCC -c dtnetwork1 -ccn chaincode1 -ccp /FabricNetwork/chaincode1 -ccl go 
```

### Interact with the network as peer0.org1
```
export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=$PWD/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051
```

### Interact with the network as peer0.org2
```
export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=$PWD/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org2MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
export CORE_PEER_ADDRESS=localhost:9051
```

### InitLedger
```
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" -C dtnetwork1 -n chaincode1 --peerAddresses localhost:7051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost:9051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt" -c '{"function":"InitLedger","Args":[]}'
```

### Query Assets
```
peer chaincode query -C dtnetwork1 -n chaincode1 -c '{"Args":["GetAllAssets"]}' | jq
peer chaincode query -C dtnetwork1 -n chaincode1 -c '{"Args":["GetAllDevices"]}' | jq
peer chaincode query -C dtnetwork1 -n chaincode1 -c '{"Args":["GetAllAriesAgents"]}' | jq
peer chaincode query -C dtnetwork1 -n chaincode1 -c '{"Args":["GetAllDeviceModels"]}' | jq
```
### BuyDevice
```
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" -C dtnetwork1 -n chaincode1 --peerAddresses localhost:7051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost
```
