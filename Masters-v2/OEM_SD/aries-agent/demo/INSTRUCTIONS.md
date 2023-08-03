Initiate Consortium agent with indy LEDGER_URL, it creates a public DID, creates OEM schema/cred def, creates SD and GW schema/cred def
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run consortium

Inititate OEM agent with indy LEDGER_URL and CONS_PUB_DID, it will connect to consortium via implicit invitation
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io CONS_PUB_DID=QnuPwPBSnrFjTzLJkrWpk9 ./run oemv2

Then Consortium issue a OEM credential to OEM
click 1 in Consortium terminal providing the connection ID with the OEM

Then Consortium request proof of OEM credential to OEM
click 2 in Consortium terminal

Initiate GW agent with indy LEDGER_URL and OEM_PUB_DID, GW will send automatically his uuid
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io OEM_PUB_DID=5ivVzac9AupaGkfFiqudtW ./run gatewayv2

Then OEM issue a GW credential to GW with uuid received
click 3a to see all connections
click 1a to issue a GW credential providing connection ID with the GW and GW uuid

Then OEM request proof of GW credential to GW
click 2 in OEM terminal

Initiate SD agent with indy LEDGER_URL and OEM_PUB_DID, 
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io OEM_PUB_DID=5ivVzac9AupaGkfFiqudtW ./run smartdevice

Then OEM issue a SD credential to SD with uuid received
click 3a to see all connections
click 1a to issue a SD credential providing connection ID with the SD and SD uuid

Then OEM request proof of SD credential to SD
click 2 in OEM terminal


Initiate Alice Agent
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run alice

Buy SD or GW, provide OEM PUB DID and deviceUUID, to start a communication with OEM

OEM issues ownership credential to alice

OEM send ownership proof request


GW generate QRCode

ALice CLain Device providing gw qr code

GW could send a ownership proof request
OEM could send a ownership proof request
