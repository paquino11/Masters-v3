import * as grpc from '@grpc/grpc-js';
import { connect, Contract, Identity, Signer, signers } from '@hyperledger/fabric-gateway';
import * as crypto from 'crypto';
import { promises as fs } from 'fs';
import * as path from 'path';
import { TextDecoder } from 'util';
import express, { Request, Response } from 'express';
import bodyParser from 'body-parser';


const app = express();
app.use(bodyParser.json());


const channelName = envOrDefault('CHANNEL_NAME', 'dtnetwork1');
const chaincodeName = envOrDefault('CHAINCODE_NAME', 'chaincode1');
const mspId = envOrDefault('MSP_ID', 'Org1MSP');

// Path to crypto materials.
const cryptoPath = envOrDefault('CRYPTO_PATH', path.resolve(__dirname, '..', '..', '..', 'test-network', 'organizations', 'peerOrganizations', 'org1.example.com'));

// Path to user private key directory.
const keyDirectoryPath = envOrDefault('KEY_DIRECTORY_PATH', path.resolve(cryptoPath, 'users', 'User1@org1.example.com', 'msp', 'keystore'));

// Path to user certificate.
const certPath = envOrDefault('CERT_PATH', path.resolve(cryptoPath, 'users', 'User1@org1.example.com', 'msp', 'signcerts', 'cert.pem'));

// Path to peer tls certificate.
const tlsCertPath = envOrDefault('TLS_CERT_PATH', path.resolve(cryptoPath, 'peers', 'peer0.org1.example.com', 'tls', 'ca.crt'));

// Gateway peer endpoint.
const peerEndpoint = 'peer0.org1.example.com:7051';

// Gateway peer SSL host name override.
const peerHostAlias = envOrDefault('PEER_HOST_ALIAS', 'peer0.org1.example.com');

const utf8Decoder = new TextDecoder();
const assetId = `agent${Date.now()}`;



async function main(): Promise<void> {

    await displayInputParameters();

    // The gRPC client connection should be shared by all Gateway connections to this endpoint.
    const client = await newGrpcConnection();

    const gateway = connect({
        client,
        identity: await newIdentity(),
        signer: await newSigner(),
        // Default timeouts for different gRPC calls
        evaluateOptions: () => {
            return { deadline: Date.now() + 5000 }; // 5 seconds
        },
        endorseOptions: () => {
            return { deadline: Date.now() + 15000 }; // 15 seconds
        },
        submitOptions: () => {
            return { deadline: Date.now() + 5000 }; // 5 seconds
        },
        commitStatusOptions: () => {
            return { deadline: Date.now() + 60000 }; // 1 minute
        },
    });

    

    try {
        // Get a network instance representing the channel where the smart contract is deployed.
        const network = gateway.getNetwork(channelName);
        console.log("hello")
        console.log(network)

        // Get the smart contract from the network.
        const contract = network.getContract(chaincodeName);
        console.log(network)

        app.post('/regdataset', async (req: Request, res: Response) => {
            const receivedString = req.body.string;
            console.log(`Received ipfs hash from client: ${receivedString}`);
            await BatchRegistration(contract, receivedString);
            res.sendStatus(200);
        });

        app.post('/regariesagent', async (req: Request, res: Response) => {
            //const receivedString = req.body.string;
            //console.log(`Received ipfs hash from client: ${receivedString}`);
            await AgentRegistration(contract);
            res.sendStatus(200);
        });

        app.post('/regdevmodel', async (req: Request, res: Response) => {
            const receivedString = req.body.string;
            console.log(`Received ipfs hash from client: ${receivedString}`);
            await DeviceModelRegistration(contract, "devmodel1345132");
            res.sendStatus(200);
        });

          
          
        app.listen(3025, () => {
            console.log('Server is running on port 3025');
        });

        await initLedger(contract);



    } finally {
        //gateway.close();
        //client.close();
    }
}

main().catch(error => {
    console.error('******** FAILED to run the application:', error);
    process.exitCode = 1;
});

async function newGrpcConnection(): Promise<grpc.Client> {
    const tlsRootCert = await fs.readFile(tlsCertPath);
    const tlsCredentials = grpc.credentials.createSsl(tlsRootCert);
    return new grpc.Client(peerEndpoint, tlsCredentials, {
        'grpc.ssl_target_name_override': peerHostAlias,
    });
}

async function newIdentity(): Promise<Identity> {
    const credentials = await fs.readFile(certPath);
    return { mspId, credentials };
}

async function newSigner(): Promise<Signer> {
    const files = await fs.readdir(keyDirectoryPath);
    const keyPath = path.resolve(keyDirectoryPath, files[0]);
    const privateKeyPem = await fs.readFile(keyPath);
    const privateKey = crypto.createPrivateKey(privateKeyPem);
    return signers.newPrivateKeySigner(privateKey);
}

/**
 * This type of transaction would typically only be run once by an application the first time it was started after its
 * initial deployment. A new version of the chaincode deployed later would likely not need to run an "init" function.
 */
async function initLedger(contract: Contract): Promise<void> {
    console.log('\n--> Submit Transaction: InitLedger, function creates the initial set of assets on the ledger');

    await contract.submitTransaction('InitLedger');

    console.log('*** Transaction committed successfully');
}

async function BatchRegistration(contract: Contract, ipfshash: string): Promise<void> {
    const batchId = `batch${Date.now()}`;
    console.log('\n--> Submit Transaction: Register Batch');
    await contract.submitTransaction(
        'BatchRegistration',
        batchId,
        'URL123',
        ipfshash,

    );

    console.log('*** Transaction committed successfully');
}

async function AgentRegistration(contract: Contract): Promise<void> {
    console.log('\n--> Submit Transaction: AgentRegistration, creates new Aries Agent on Fabric');

    await contract.submitTransaction(
        'AgentRegistration',
        'did:sov:oem',
        'OEM',
        'IN_GOOD_STANDING',
    );

    console.log('*** Transaction committed successfully');
}

async function DeviceModelRegistration(contract: Contract, devmodel: string): Promise<void> {
    console.log('\n--> Submit Transaction: DeviceModelRegistration, creates new Aries Agent on Fabric');

    await contract.submitTransaction(
        'DeviceModelRegistration',
        devmodel,
        'super device model'
    );

    console.log('*** Transaction committed successfully');
}


/**
 * Evaluate a transaction to query ledger state.
 */
/*async function getAllAssets(contract: Contract): Promise<void> {
    console.log('\n--> Evaluate Transaction: GetAllAssets, function returns all the current assets on the ledger');

    const resultBytes = await contract.evaluateTransaction('GetAllAssets');

    const resultJson = utf8Decoder.decode(resultBytes);
    const result = JSON.parse(resultJson);
    console.log('*** Result:', result);
}*/

/**
 * Submit a transaction synchronously, blocking until it has been committed to the ledger.
 */
async function createAsset(contract: Contract): Promise<void> {
    console.log('\n--> Submit Transaction: CreateAsset, creates new asset with ID, Color, Size, Owner and AppraisedValue arguments');

    await contract.submitTransaction(
        'CreateAsset',
        assetId,
        'yellow',
        '5',
        'Tom',
        '1300',
    );

    console.log('*** Transaction committed successfully');
}


async function DeviceGenesisRegistration(contract: Contract): Promise<void> {
    console.log('\n--> Submit Transaction: DeviceGenesisRegistration, creates new Device on Fabric');

    await contract.submitTransaction(
        'DeviceGenesisRegistration',
        'device2',
        'OEM',
        'iWatchModel',
        'SD',
        'AVAILABLE',
        '',
        '',
    );

    console.log('*** Transaction committed successfully');
}

async function BuyDevice(contract: Contract): Promise<void> {
    console.log('\n--> Submit Transaction: BuyDevice');

    await contract.submitTransaction(
        'BuyDevice',
        'device2',
        'IN_TRANSIT',
    );

    console.log('*** Transaction committed successfully');
}

async function ClaimDevice(contract: Contract): Promise<void> {
    console.log('\n--> Submit Transaction: ClaimDevice');

    await contract.submitTransaction(
        'ClaimDevice',
        'device2',
        'CLAIMED',
        'controllerUUID',
    );

    console.log('*** Transaction committed successfully');
}

async function TwinDevice(contract: Contract): Promise<void> {
    console.log('\n--> Submit Transaction: TwinDevice');

    await contract.submitTransaction(
        'TwinDevice',
        'device2',
        'TWINNED',
        'DTID1',
    );

    console.log('*** Transaction committed successfully');
}

async function UntwinDevice(contract: Contract): Promise<void> {
    console.log('\n--> Submit Transaction: UntwinDevice');

    await contract.submitTransaction(
        'UntwinDevice',
        'device2',
        'CLAIMED',
        'DTID1',
    );

    console.log('*** Transaction committed successfully');
}

async function SellDevice(contract: Contract): Promise<void> {
    console.log('\n--> Submit Transaction: SellDevice');

    await contract.submitTransaction(
        'SellDevice',
        'device2',
        'AVAILABLE',
    );

    console.log('*** Transaction committed successfully');
}


/**
 * Submit transaction asynchronously, allowing the application to process the smart contract response (e.g. update a UI)
 * while waiting for the commit notification.
 */
async function transferAssetAsync(contract: Contract): Promise<void> {
    console.log('\n--> Async Submit Transaction: TransferAsset, updates existing asset owner');

    const commit = await contract.submitAsync('TransferAsset', {
        arguments: [assetId, 'Saptha'],
    });
    const oldOwner = utf8Decoder.decode(commit.getResult());

    console.log(`*** Successfully submitted transaction to transfer ownership from ${oldOwner} to Saptha`);
    console.log('*** Waiting for transaction commit');

    const status = await commit.getStatus();
    if (!status.successful) {
        throw new Error(`Transaction ${status.transactionId} failed to commit with status code ${status.code}`);
    }

    console.log('*** Transaction committed successfully');
}

async function readAssetByID(contract: Contract): Promise<void> {
    console.log('\n--> Evaluate Transaction: ReadAsset, function returns asset attributes');

    const resultBytes = await contract.evaluateTransaction('ReadAsset', assetId);

    const resultJson = utf8Decoder.decode(resultBytes);
    const result = JSON.parse(resultJson);
    console.log('*** Result:', result);
}

/**
 * submitTransaction() will throw an error containing details of any error responses from the smart contract.
 */
async function updateNonExistentAsset(contract: Contract): Promise<void>{
    console.log('\n--> Submit Transaction: UpdateAsset asset70, asset70 does not exist and should return an error');

    try {
        await contract.submitTransaction(
            'UpdateAsset',
            'asset70',
            'blue',
            '5',
            'Tomoko',
            '300',
        );
        console.log('******** FAILED to return an error');
    } catch (error) {
        console.log('*** Successfully caught the error: \n', error);
    }
}

async function getAllAriesAgent(contract: Contract): Promise<void> {
    console.log('\n--> Evaluate Transaction: GetAllAriesAgents, function returns all the current Aries Agents on the ledger');

    const resultBytes = await contract.evaluateTransaction('GetAllAriesAgents');

    const resultJson = utf8Decoder.decode(resultBytes);
    const result = JSON.parse(resultJson);
    console.log('*** Result:', result);
}

async function getAllDeviceModels(contract: Contract): Promise<void> {
    console.log('\n--> Evaluate Transaction: GetAllDeviceModels, function returns all the current Device Models on the ledger');

    const resultBytes = await contract.evaluateTransaction('GetAllDeviceModels');

    const resultJson = utf8Decoder.decode(resultBytes);
    const result = JSON.parse(resultJson);
    console.log('*** Result:', result);
}

async function getAllDevices(contract: Contract): Promise<void> {
    console.log('\n--> Evaluate Transaction: GetAllDevices, function returns all the current Devices on the ledger');

    const resultBytes = await contract.evaluateTransaction('GetAllDevices');

    const resultJson = utf8Decoder.decode(resultBytes);
    const result = JSON.parse(resultJson);
    console.log('*** Result:', result);
}

async function getAllBatchs(contract: Contract): Promise<void> {
    console.log('\n--> Evaluate Transaction: GetAllDataBatchs, function returns all the current Data Batchs on the ledger');

    const resultBytes = await contract.evaluateTransaction('GetAllDataBatchs');

    const resultJson = utf8Decoder.decode(resultBytes);
    const result = JSON.parse(resultJson);
    console.log('*** Result:', result);
}




/**
 * envOrDefault() will return the value of an environment variable, or a default vavavariable is undefined.
 */
function envOrDefault(key: string, defaultValue: string): string {
    return process.env[key] || defaultValue;
}

/**
 * displayInputParameters() will print the global scope parameters used by the main driver routine.
 */
async function displayInputParameters(): Promise<void> {
    console.log(`channelName:       ${channelName}`);
    console.log(`chaincodeName:     ${chaincodeName}`);
    console.log(`mspId:             ${mspId}`);
    console.log(`cryptoPath:        ${cryptoPath}`);
    console.log(`keyDirectoryPath:  ${keyDirectoryPath}`);
    console.log(`certPath:          ${certPath}`);
    console.log(`tlsCertPath:       ${tlsCertPath}`);
    console.log(`peerEndpoint:      ${peerEndpoint}`);
    console.log(`peerHostAlias:     ${peerHostAlias}`);
}