import asyncio
import base64
import binascii
import json
import logging
import os
import sys
import time
import datetime
from urllib.parse import urlparse
import uuid
import subprocess
import os

from aiohttp import ClientError
from qrcode import QRCode

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runners.agent_container import (  # noqa:E402
    arg_parser,
    create_agent_with_args,
    AriesAgent,
)
from runners.support.agent import (  # noqa:E402
    CRED_FORMAT_INDY,
    CRED_FORMAT_JSON_LD,
    SIG_TYPE_BLS,
    OEM_PUB_DID,
)
from runners.support.utils import (  # noqa:E402
    check_requires,
    log_msg,
    log_status,
    log_timer,
    prompt,
    prompt_loop,
)


CRED_PREVIEW_TYPE = "https://didcomm.org/issue-credential/2.0/credential-preview"
SELF_ATTESTED = os.getenv("SELF_ATTESTED")
TAILS_FILE_COUNT = int(os.getenv("TAILS_FILE_COUNT", 100))

logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger(__name__)


class GatewayAgent(AriesAgent):
    def __init__(
        self,
        ident: str,
        http_port: int,
        admin_port: int,
        no_auto: bool = False,
        endorser_role: str = None,
        revocation: bool = False,
        **kwargs,
    ):
        super().__init__(
            ident,
            http_port,
            admin_port,
            prefix="GATEWAY",
            no_auto=no_auto,
            endorser_role=endorser_role,
            revocation=revocation,
            **kwargs,
        )
        self.connection_id = None
        self._connection_ready = None
        self.cred_state = {}
        # TODO define a dict to hold credential attributes
        # based on cred_def_id
        self.cred_attrs = {}

    async def detect_connection(self):
        await self._connection_ready
        self._connection_ready = None

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()


    def generate_proof_request_web_request_ownership(
        self, aip, cred_type, revocation, exchange_tracing, connectionless=False
    ):
        age = 0
        d = datetime.date.today()
        birth_date = datetime.date(d.year - age, d.month, d.day)
        birth_date_format = "%Y%m%d"
        if aip == 10:
            req_attrs = [
                {
                    "name": "name",
                    "restrictions": [{"schema_name": "sd_gw_schema"}],
                },
                {
                    "name": "model",
                    "restrictions": [{"schema_name": "sd_gw_schema"}],
                },
            ]
            if revocation:
                req_attrs.append(
                    {
                        "name": "model",
                        "restrictions": [{"schema_name": "sd_gw_schema"}],
                        "non_revoked": {"to": int(time.time() - 1)},
                    },
                )
            else:
                req_attrs.append(
                    {
                        "name": "model",
                        "restrictions": [{"schema_name": "sd_gw_schema"}],
                    }
                )
            if SELF_ATTESTED:
                # test self-attested claims
                req_attrs.append(
                    {"name": "self_attested_thing"},
                )
            req_preds = [
                # test zero-knowledge proofs
                {
                    "name": "manufacture_date",
                    "p_type": "<=",
                    "p_value": int(birth_date.strftime(birth_date_format)),
                    "restrictions": [{"schema_name": "sd_gw_schema"}],
                },
                {
                    "name": "model",
                    "p_type": "=",
                    "p_value": "GW/SDModel",
                    "restrictions": [{"schema_name": "sd_gw_schema"}],
                },
            ]
            indy_proof_request = {
                "name": "Proof of Gateway or SmartDevice",
                "version": "1.0",
                "requested_attributes": {
                    f"0_{req_attr['name']}_uuid": req_attr for req_attr in req_attrs
                },
                "requested_predicates": {
                    f"0_{req_pred['name']}_GE_uuid": req_pred for req_pred in req_preds
                },
            }

            if revocation:
                indy_proof_request["non_revoked"] = {"to": int(time.time())}

            proof_request_web_request = {
                "proof_request": indy_proof_request,
                "trace": exchange_tracing,
            }
            if not connectionless:
                proof_request_web_request["connection_id"] = self.connection_id
            return proof_request_web_request

        elif aip == 20:
            if cred_type == CRED_FORMAT_INDY:
                req_attrs = [
                    {
                        "name": "deviceUUID",
                        "restrictions": [{"schema_name": "ownership_schema"}],
                    },
                    {
                        "name": "model",
                        "restrictions": [{"schema_name": "ownership_schema"}],
                    },
                ]
                if revocation:
                    req_attrs.append(
                        {
                            "name": "model",
                            "restrictions": [{"schema_name": "ownership_schema"}],
                            "non_revoked": {"to": int(time.time() - 1)},
                        },
                    )
                else:
                    req_attrs.append(
                        {
                            "name": "model",
                            "restrictions": [{"schema_name": "ownership_schema"}],
                        }
                    )
                if SELF_ATTESTED:
                    # test self-attested claims
                    req_attrs.append(
                        {"name": "self_attested_thing"},
                    )
                req_preds = [
                    # test zero-knowledge proofs
                    {
                        "name": "ownership_date",
                        "p_type": "<=",
                        "p_value": int(birth_date.strftime(birth_date_format)),
                        "restrictions": [{"schema_name": "ownership_schema"}],
                    }
                ]
                indy_proof_request = {
                    "name": "Proof of Ownership",
                    "version": "1.0",
                    "requested_attributes": {
                        f"0_{req_attr['name']}_uuid": req_attr for req_attr in req_attrs
                    },
                    "requested_predicates": {
                        f"0_{req_pred['name']}_GE_uuid": req_pred
                        for req_pred in req_preds
                    },
                }

                if revocation:
                    indy_proof_request["non_revoked"] = {"to": int(time.time())}

                proof_request_web_request = {
                    "presentation_request": {"indy": indy_proof_request},
                    "trace": exchange_tracing,
                }
                if not connectionless:
                    proof_request_web_request["connection_id"] = self.connection_id
                return proof_request_web_request

            elif cred_type == CRED_FORMAT_JSON_LD:
                proof_request_web_request = {
                    "comment": "test proof request for json-ld",
                    "presentation_request": {
                        "dif": {
                            "options": {
                                "challenge": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                                "domain": "4jt78h47fh47",
                            },
                            "presentation_definition": {
                                "id": "32f54163-7166-48f1-93d8-ff217bdb0654",
                                "format": {"ldp_vp": {"proof_type": [SIG_TYPE_BLS]}},
                                "input_descriptors": [
                                    {
                                        "id": "citizenship_input_1",
                                        "name": "EU Driver's License",
                                        "schema": [
                                            {
                                                "uri": "https://www.w3.org/2018/credentials#VerifiableCredential"
                                            },
                                            {
                                                "uri": "https://w3id.org/citizenship#PermanentResident"
                                            },
                                        ],
                                        "constraints": {
                                            "limit_disclosure": "required",
                                            "is_holder": [
                                                {
                                                    "directive": "required",
                                                    "field_id": [
                                                        "1f44d55f-f161-4938-a659-f8026467f126"
                                                    ],
                                                }
                                            ],
                                            "fields": [
                                                {
                                                    "id": "1f44d55f-f161-4938-a659-f8026467f126",
                                                    "path": [
                                                        "$.credentialSubject.familyName"
                                                    ],
                                                    "purpose": "The claim must be from one of the specified person",
                                                    "filter": {"const": "SMITH"},
                                                },
                                                {
                                                    "path": [
                                                        "$.credentialSubject.givenName"
                                                    ],
                                                    "purpose": "The claim must be from one of the specified person",
                                                },
                                            ],
                                        },
                                    }
                                ],
                            },
                        }
                    },
                }
                if not connectionless:
                    proof_request_web_request["connection_id"] = self.connection_id
                return proof_request_web_request

            else:
                raise Exception(f"Error invalid credential type: {self.cred_type}")

        else:
            raise Exception(f"Error invalid AIP level: {self.aip}")


async def input_invitation(agent_container):
    agent_container.agent._connection_ready = asyncio.Future()
    async for details in prompt_loop("Invite details: "):
        b64_invite = None
        try:
            url = urlparse(details)
            query = url.query
            if query and "c_i=" in query:
                pos = query.index("c_i=") + 4
                b64_invite = query[pos:]
            elif query and "oob=" in query:
                pos = query.index("oob=") + 4
                b64_invite = query[pos:]
            else:
                b64_invite = details
        except ValueError:
            b64_invite = details

        if b64_invite:
            try:
                padlen = 4 - len(b64_invite) % 4
                if padlen <= 2:
                    b64_invite += "=" * padlen
                invite_json = base64.urlsafe_b64decode(b64_invite)
                details = invite_json.decode("utf-8")
            except binascii.Error:
                pass
            except UnicodeDecodeError:
                pass

        if details:
            try:
                details = json.loads(details)
                break
            except json.JSONDecodeError as e:
                log_msg("Invalid invitation:", str(e))

    with log_timer("Connect duration:"):
        connection = await agent_container.input_invitation(details, wait=True)


async def main(args):
    print(OEM_PUB_DID)
    gateway_agent = await create_agent_with_args(args, ident="gateway")

    async def check_for_new_connection(n, lr):
        response = await gateway_agent.agent.admin_GET(f"/connections")
        n_results = len(response["results"])
        #print(oem_agent.agent.lastmessage)
        last_result = lr
        newconnect = False
        if n < n_results:
            n += 1
            print("New Connection")
            last_result = response["results"][-1]  # get the last element of the 'results' array
            time.sleep(3)
            newconnect = True
            uuid_obj = uuid.uuid4()
            uuid_str = str(uuid_obj)
            msg = uuid_str
            gateway_agent.agent.connection_id = last_result["connection_id"]  # get the value of the 'connection_id' field

        return n, last_result, response, newconnect   # always return the value of n
    

    try:
        log_status(
            "#1 Provision an agent and wallet, get back configuration details"
            + (
                f" (Wallet type: {gateway_agent.wallet_type})"
                if gateway_agent.wallet_type
                else ""
            )
        )
        agent = GatewayAgent(
            "gateway.agent",
            gateway_agent.start_port,
            gateway_agent.start_port + 1,
            genesis_data=gateway_agent.genesis_txns,
            genesis_txn_list=gateway_agent.genesis_txn_list,
            no_auto=gateway_agent.no_auto,
            tails_server_base_url=gateway_agent.tails_server_base_url,
            revocation=gateway_agent.revocation,
            timing=gateway_agent.show_timing,
            multitenant=gateway_agent.multitenant,
            mediation=gateway_agent.mediation,
            wallet_type=gateway_agent.wallet_type,
            seed=gateway_agent.seed,
            aip=gateway_agent.aip,
            endorser_role=gateway_agent.endorser_role,
        )

        ##await gateway_agent.initialize(the_agent=agent)
        
        if gateway_agent.cred_type == CRED_FORMAT_INDY:
            gateway_agent.public_did = True
            await gateway_agent.initialize(
                the_agent=agent,
                create_endorser_agent=(gateway_agent.endorser_role == "author")
                if gateway_agent.endorser_role
                else False,
            )
        elif gateway_agent.cred_type == CRED_FORMAT_JSON_LD:
            gateway_agent.public_did = True
            await gateway_agent.initialize(the_agent=agent)
        else:
            raise Exception("Invalid credential type:" + gateway_agent.cred_type)
        
        if OEM_PUB_DID != None:
            log_status("Implicit Invitation to Consortium.\nConsortium Pub DID: "+ OEM_PUB_DID)
            implicit_invitation = await gateway_agent.agent.admin_POST(f"/didexchange/create-request?their_public_did={OEM_PUB_DID}&use_public_did=true")
            connectionid = implicit_invitation['connection_id']
            gateway_agent.agent.connection_id = connectionid
            print(connectionid)

        uuid_obj = uuid.uuid4()
        uuid_str = str(uuid_obj)
        msg = uuid_str
        print("UUID: "+ msg)
        time.sleep(1) 
        if OEM_PUB_DID != None:
            await gateway_agent.agent.admin_POST(
                f"/connections/{gateway_agent.agent.connection_id}/send-message",
                {"content": msg})
        
        exchange_tracing = False
        options = (
            "    (2c) Send Ownership Proof Request\n"
 #           "    (2a) Send *Connectionless* Proof Request (requires a Mobile client)\n"
            "    (3) Send Message\n"
            "    (3a) Get All Connections\n"
            "    (4a) GW QR Code\n"
            "    (4b) Input New Invitation\n"
        )
        if gateway_agent.revocation:
            options += "    (5) Revoke Credential\n" "    (6) Publish Revocations\n"
        if gateway_agent.endorser_role and gateway_agent.endorser_role == "author":
            options += "    (D) Set Endorser's DID\n"
        if gateway_agent.multitenant:
            options += "    (W) Create and/or Enable Wallet\n"
#        options += "    (T) Toggle tracing on credential/proof exchange\n"
        options += "    (X) Exit?\n[1/2/3/4/{}{}T/X] ".format(
            "5/6/" if gateway_agent.revocation else "",
            "W/" if gateway_agent.multitenant else "",
        )
        async for option in prompt_loop(options):
        
            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break

            elif option in "dD" and gateway_agent.endorser_role:
                endorser_did = await prompt("Enter Endorser's DID: ")
                await gateway_agent.agent.admin_POST(
                    f"/transactions/{gateway_agent.agent.connection_id}/set-endorser-info",
                    params={"endorser_did": endorser_did},
                )

            elif option in "wW" and gateway_agent.multitenant:
                target_wallet_name = await prompt("Enter wallet name: ")
                include_subwallet_webhook = await prompt(
                    "(Y/N) Create sub-wallet webhook target: "
                )
                if include_subwallet_webhook.lower() == "y":
                    created = await gateway_agent.agent.register_or_switch_wallet(
                        target_wallet_name,
                        webhook_port=gateway_agent.agent.get_new_webhook_port(),
                        public_did=True,
                        mediator_agent=gateway_agent.mediator_agent,
                        endorser_agent=gateway_agent.endorser_agent,
                        taa_accept=gateway_agent.taa_accept,
                    )
                else:
                    created = await gateway_agent.agent.register_or_switch_wallet(
                        target_wallet_name,
                        public_did=True,
                        mediator_agent=gateway_agent.mediator_agent,
                        endorser_agent=gateway_agent.endorser_agent,
                        cred_type=gateway_agent.cred_type,
                        taa_accept=gateway_agent.taa_accept,
                    )
                # create a schema and cred def for the new wallet
                # TODO check first in case we are switching between existing wallets


            elif option in "tT":
                exchange_tracing = not exchange_tracing
                log_msg(
                    ">>> Credential/Proof Exchange Tracing is {}".format(
                        "ON" if exchange_tracing else "OFF"
                    )
                )

            elif option == "1a": #issue credential
                log_status("#13 Issue credential offer to X")
                gateway_agent.agent.connection_id = await prompt("Enter connection ID: ")
                uuid1 = await prompt("Enter EGW/SD uuid1: ")
                if gateway_agent.aip == 10:
                    offer_request = gateway_agent.agent.generate_gw_credential_offer(
                        gateway_agent.aip, None, gateway_agent.cred_def_id, exchange_tracing, uuid1
                    )
                    await gateway_agent.agent.admin_POST(
                        "/issue-credential/send-offer", offer_request
                    )

                elif gateway_agent.aip == 20:
                    if gateway_agent.cred_type == CRED_FORMAT_INDY:
                        offer_request = gateway_agent.agent.generate_gw_credential_offer(
                            gateway_agent.aip,
                            gateway_agent.cred_type,
                            gateway_agent.cred_def_id,
                            exchange_tracing,
                            uuid1,
                        )

                    elif gateway_agent.cred_type == CRED_FORMAT_JSON_LD:
                        offer_request = gateway_agent.agent.generate_gw_credential_offer(
                            gateway_agent.aip,
                            gateway_agent.cred_type,
                            None,
                            exchange_tracing,
                        )

                    else:
                        raise Exception(
                            f"Error invalid credential type: {gateway_agent.cred_type}"
                        )

                    await gateway_agent.agent.admin_POST(
                        "/issue-credential-2.0/send-offer", offer_request
                    )

                else:
                    raise Exception(f"Error invalid AIP level: {gateway_agent.aip}")
            elif option == "1b":
                log_status("#13 Issue credential offer to X")
                gateway_agent.agent.connection_id = await prompt("Enter connection ID: ")
                uuid1 = await prompt("Enter EGW/SD uuid1: ")
                if gateway_agent.aip == 10:
                    offer_request = gateway_agent.agent.generate_sd_credential_offer(
                        gateway_agent.aip, None, gateway_agent.cred_def_id, exchange_tracing
                    )
                    await gateway_agent.agent.admin_POST(
                        "/issue-credential/send-offer", offer_request
                    )

                elif gateway_agent.aip == 20:
                    if gateway_agent.cred_type == CRED_FORMAT_INDY:
                        offer_request = gateway_agent.agent.generate_ownership_credential_offer(
                            gateway_agent.aip,
                            gateway_agent.cred_type,
                            gateway_agent.cred_def_id_ownership,
                            exchange_tracing,
                            uuid1,
                        )

                    elif gateway_agent.cred_type == CRED_FORMAT_JSON_LD:
                        offer_request = gateway_agent.agent.generate_sd_credential_offer(
                            gateway_agent.aip,
                            gateway_agent.cred_type,
                            None,
                            exchange_tracing,
                        )

                    else:
                        raise Exception(
                            f"Error invalid credential type: {gateway_agent.cred_type}"
                        )

                    await gateway_agent.agent.admin_POST(
                        "/issue-credential-2.0/send-offer", offer_request
                    )

                else:
                    raise Exception(f"Error invalid AIP level: {gateway_agent.aip}")
            elif option == "1c":
                log_status("#13 Issue credential offer to X")
                gateway_agent.agent.connection_id = await prompt("Enter connection ID: ")
                uuid1 = await prompt("Enter EGW/SD uuid1: ")
                if gateway_agent.aip == 10:
                    offer_request = gateway_agent.agent.generate_sd_credential_offer(
                        gateway_agent.aip, None, gateway_agent.cred_def_id, exchange_tracing
                    )
                    await gateway_agent.agent.admin_POST(
                        "/issue-credential/send-offer", offer_request
                    )

                elif gateway_agent.aip == 20:
                    if gateway_agent.cred_type == CRED_FORMAT_INDY:
                        offer_request = gateway_agent.agent.generate_ownership_credential_offer(
                            gateway_agent.aip,
                            gateway_agent.cred_type,
                            #gateway_agent.cred_def_id,
                            gateway_agent.cred_def_id_ownership,
                            exchange_tracing,
                            uuid1
                        )

                    elif gateway_agent.cred_type == CRED_FORMAT_JSON_LD:
                        offer_request = gateway_agent.agent.generate_sd_credential_offer(
                            gateway_agent.aip,
                            gateway_agent.cred_type,
                            None,
                            exchange_tracing,
                        )

                    else:
                        raise Exception(
                            f"Error invalid credential type: {gateway_agent.cred_type}"
                        )

                    await gateway_agent.agent.admin_POST(
                        "/issue-credential-2.0/send-offer", offer_request
                    )

                else:
                    raise Exception(f"Error invalid AIP level: {gateway_agent.aip}")

            elif option == "2":
                log_status("#20 Request proof of oem")
                if gateway_agent.aip == 10:
                    proof_request_web_request = (
                        gateway_agent.agent.generate_proof_request_web_request(
                            gateway_agent.aip,
                            gateway_agent.cred_type,
                            gateway_agent.revocation,
                            exchange_tracing,
                        )
                    )
                    await gateway_agent.agent.admin_POST(
                        "/present-proof/send-request", proof_request_web_request
                    )
                    pass

                elif gateway_agent.aip == 20:
                    if gateway_agent.cred_type == CRED_FORMAT_INDY:
                        proof_request_web_request = (
                            gateway_agent.agent.generate_proof_request_web_request_ownership(
                                gateway_agent.aip,
                                gateway_agent.cred_type,
                                gateway_agent.revocation,
                                exchange_tracing,
                            )
                        )

                    elif gateway_agent.cred_type == CRED_FORMAT_JSON_LD:
                        proof_request_web_request = (
                            gateway_agent.agent.generate_proof_request_web_request(
                                gateway_agent.aip,
                                gateway_agent.cred_type,
                                gateway_agent.revocation,
                                exchange_tracing,
                            )
                        )

                    else:
                        raise Exception(
                            "Error invalid credential type:" + gateway_agent.cred_type
                        )

                    await agent.admin_POST(
                        "/present-proof-2.0/send-request", proof_request_web_request
                    )

                else:
                    raise Exception(f"Error invalid AIP level: {gateway_agent.aip}")
            
            elif option == "2c":
                log_status("#20 Request proof of ownership")
                if gateway_agent.aip == 10:
                    proof_request_web_request = (
                        gateway_agent.agent.generate_proof_request_web_request(
                            gateway_agent.aip,
                            gateway_agent.cred_type,
                            gateway_agent.revocation,
                            exchange_tracing,
                        )
                    )
                    await gateway_agent.agent.admin_POST(
                        "/present-proof/send-request", proof_request_web_request
                    )
                    pass

                elif gateway_agent.aip == 20:
                    if gateway_agent.cred_type == CRED_FORMAT_INDY:
                        proof_request_web_request = (
                            gateway_agent.agent.generate_proof_request_web_request_ownership(
                                gateway_agent.aip,
                                gateway_agent.cred_type,
                                gateway_agent.revocation,
                                exchange_tracing,
                            )
                        )

                    elif gateway_agent.cred_type == CRED_FORMAT_JSON_LD:
                        proof_request_web_request = (
                            gateway_agent.agent.generate_proof_request_web_request(
                                gateway_agent.aip,
                                gateway_agent.cred_type,
                                gateway_agent.revocation,
                                exchange_tracing,
                            )
                        )

                    else:
                        raise Exception(
                            "Error invalid credential type:" + gateway_agent.cred_type
                        )

                    await agent.admin_POST(
                        "/present-proof-2.0/send-request", proof_request_web_request
                    )

                else:
                    raise Exception(f"Error invalid AIP level: {gateway_agent.aip}")

            elif option == "2a":
                log_status("#20 Request * Connectionless * proof of oem")
                if gateway_agent.aip == 10:
                    proof_request_web_request = (
                        gateway_agent.agent.generate_proof_request_web_request(
                            gateway_agent.aip,
                            gateway_agent.cred_type,
                            gateway_agent.revocation,
                            exchange_tracing,
                            connectionless=True,
                        )
                    )
                    proof_request = await gateway_agent.agent.admin_POST(
                        "/present-proof/create-request", proof_request_web_request
                    )
                    pres_req_id = proof_request["presentation_exchange_id"]
                    url = (
                        os.getenv("WEBHOOK_TARGET")
                        or (
                            "http://"
                            + os.getenv("DOCKERHOST").replace(
                                "{PORT}", str(gateway_agent.agent.admin_port + 1)
                            )
                            + "/webhooks"
                        )
                    ) + f"/pres_req/{pres_req_id}/"
                    log_msg(f"Proof request url: {url}")
                    qr = QRCode(border=1)
                    qr.add_data(url)
                    log_msg(
                        "Scan the following QR code to accept the proof request from a mobile agent."
                    )
                    qr.print_ascii(invert=True)

                elif gateway_agent.aip == 20:
                    if gateway_agent.cred_type == CRED_FORMAT_INDY:
                        proof_request_web_request = (
                            gateway_agent.agent.generate_proof_request_web_request(
                                gateway_agent.aip,
                                gateway_agent.cred_type,
                                gateway_agent.revocation,
                                exchange_tracing,
                                connectionless=True,
                            )
                        )
                    elif gateway_agent.cred_type == CRED_FORMAT_JSON_LD:
                        proof_request_web_request = (
                            gateway_agent.agent.generate_proof_request_web_request(
                                gateway_agent.aip,
                                gateway_agent.cred_type,
                                gateway_agent.revocation,
                                exchange_tracing,
                                connectionless=True,
                            )
                        )
                    else:
                        raise Exception(
                            "Error invalid credential type:" + gateway_agent.cred_type
                        )

                    proof_request = await gateway_agent.agent.admin_POST(
                        "/present-proof-2.0/create-request", proof_request_web_request
                    )
                    pres_req_id = proof_request["pres_ex_id"]
                    url = (
                        "http://"
                        + os.getenv("DOCKERHOST").replace(
                            "{PORT}", str(gateway_agent.agent.admin_port + 1)
                        )
                        + "/webhooks/pres_req/"
                        + pres_req_id
                        + "/"
                    )
                    log_msg(f"Proof request url: {url}")
                    qr = QRCode(border=1)
                    qr.add_data(url)
                    log_msg(
                        "Scan the following QR code to accept the proof request from a mobile agent."
                    )
                    qr.print_ascii(invert=True)
                else:
                    raise Exception(f"Error invalid AIP level: {gateway_agent.aip}")

            elif option == "3":
                gateway_agent.agent.connection_id = await prompt("Enter connection ID: ")
                msg = await prompt("Enter message: ")
                await gateway_agent.agent.admin_POST(
                    f"/connections/{gateway_agent.agent.connection_id}/send-message",
                    {"content": msg},
                )
            elif option == "3a":
                response = await gateway_agent.agent.admin_GET(f"/connections")
                print(response)
            elif option == "4a":
                log_msg(
                    "Creating a QR Code, please receive "
                    "and accept this invitation using agent"
                )
                await gateway_agent.generate_invitation(
                    display_qr=True,
                    reuse_connections=gateway_agent.reuse_connections,
                    wait=True,
                )
                time.sleep(1)
                proof_request_web_request = (
                            gateway_agent.agent.generate_proof_request_web_request_ownership(
                                gateway_agent.aip,
                                gateway_agent.cred_type,
                                gateway_agent.revocation,
                                exchange_tracing,
                            )
                        )
                await agent.admin_POST(
                        "/present-proof-2.0/send-request", proof_request_web_request
                    )
                           
            
            elif option == "4b":
                # handle new invitation
                log_status("Input new invitation details")
                await input_invitation(gateway_agent)
            elif option == "5" and gateway_agent.revocation:
                rev_reg_id = (await prompt("Enter revocation registry ID: ")).strip()
                cred_rev_id = (await prompt("Enter credential revocation ID: ")).strip()
                publish = (
                    await prompt("Publish now? [Y/N]: ", default="N")
                ).strip() in "yY"
                try:
                    await gateway_agent.agent.admin_POST(
                        "/revocation/revoke",
                        {
                            "rev_reg_id": rev_reg_id,
                            "cred_rev_id": cred_rev_id,
                            "publish": publish,
                            "connection_id": gateway_agent.agent.connection_id,
                            # leave out thread_id, let aca-py generate
                            # "thread_id": "12345678-4444-4444-4444-123456789012",
                            "comment": "Revocation reason goes here ...",
                        },
                    )
                except ClientError:
                    pass

            elif option == "6" and gateway_agent.revocation:
                try:
                    resp = await gateway_agent.agent.admin_POST(
                        "/revocation/publish-revocations", {}
                    )
                    gateway_agent.agent.log(
                        "Published revocations for {} revocation registr{} {}".format(
                            len(resp["rrid2crid"]),
                            "y" if len(resp["rrid2crid"]) == 1 else "ies",
                            json.dumps([k for k in resp["rrid2crid"]], indent=4),
                        )
                    )
                except ClientError:
                    pass

        if gateway_agent.show_timing:
            timing = await gateway_agent.agent.fetch_timing()
            if timing:
                for line in gateway_agent.agent.format_timing(timing):
                    log_msg(line)

    finally:
        terminated = await gateway_agent.terminate()

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    parser = arg_parser(ident="consortium", port=8080)
    args = parser.parse_args()

    ENABLE_PYDEVD_PYCHARM = os.getenv("ENABLE_PYDEVD_PYCHARM", "").lower()
    ENABLE_PYDEVD_PYCHARM = ENABLE_PYDEVD_PYCHARM and ENABLE_PYDEVD_PYCHARM not in (
        "false",
        "0",
    )
    PYDEVD_PYCHARM_HOST = os.getenv("PYDEVD_PYCHARM_HOST", "localhost")
    PYDEVD_PYCHARM_CONTROLLER_PORT = int(
        os.getenv("PYDEVD_PYCHARM_CONTROLLER_PORT", 5001)
    )

    if ENABLE_PYDEVD_PYCHARM:
        try:
            import pydevd_pycharm

            print(
                "Consortium remote debugging to "
                f"{PYDEVD_PYCHARM_HOST}:{PYDEVD_PYCHARM_CONTROLLER_PORT}"
            )
            pydevd_pycharm.settrace(
                host=PYDEVD_PYCHARM_HOST,
                port=PYDEVD_PYCHARM_CONTROLLER_PORT,
                stdoutToServer=True,
                stderrToServer=True,
                suspend=False,
            )
        except ImportError:
            print("pydevd_pycharm library was not found")

    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
