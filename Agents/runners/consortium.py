import asyncio
import json
import logging
import os
import sys
import time
import datetime
import subprocess

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
)
from runners.support.utils import (  # noqa:E402
    log_msg,
    log_status,
    prompt,
    prompt_loop,
)


CRED_PREVIEW_TYPE = "https://didcomm.org/issue-credential/2.0/credential-preview"
SELF_ATTESTED = os.getenv("SELF_ATTESTED")
TAILS_FILE_COUNT = int(os.getenv("TAILS_FILE_COUNT", 100))

#logging.basicConfig(level=logging.WARNING)
#LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')

class ConsortiumAgent(AriesAgent):
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
            prefix="Consortium",
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
        self.postgres=True



    async def detect_connection(self):
        await self._connection_ready
        self._connection_ready = None

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()

    def generate_credential_offer(self, aip, cred_type, cred_def_id, exchange_tracing):
        print(aip, cred_type, self.connection_id)
        age = 0
        d = datetime.date.today()
        enrollDate = datetime.date(d.year - age, d.month, d.day)
        enrollDate_format = "%Y%m%d"
        if aip == 10:
            # define attributes to send for credential
            self.cred_attrs[cred_def_id] = {
                "name": "Bosch",
                "type": "OEM",
                "enrollDate": enrollDate.strftime(enrollDate_format),
                "timestamp": str(int(time.time())),
            }

            cred_preview = {
                "@type": CRED_PREVIEW_TYPE,
                "attributes": [
                    {"name": n, "value": v}
                    for (n, v) in self.cred_attrs[cred_def_id].items()
                ],
            }
            offer_request = {
                "connection_id": self.connection_id,
                "cred_def_id": cred_def_id,
                "comment": f"Offer on cred def id {cred_def_id}",
                "auto_remove": False,
                "credential_preview": cred_preview,
                "trace": exchange_tracing,
            }
            return offer_request

        elif aip == 20:
            if cred_type == CRED_FORMAT_INDY:
                self.cred_attrs[cred_def_id] = {
                    "name": "Bosch",
                    "type": "OEM",
                    "enrollDate": enrollDate.strftime(enrollDate_format),
                    "timestamp": str(int(time.time())),
                }
                print(enrollDate.strftime(enrollDate_format))
                cred_preview = {
                    "@type": CRED_PREVIEW_TYPE,
                    "attributes": [
                        {"name": n, "value": v}
                        for (n, v) in self.cred_attrs[cred_def_id].items()
                    ],
                }
                offer_request = {
                    "connection_id": self.connection_id,
                    "comment": f"Offer on cred def id {cred_def_id}",
                    "auto_remove": False,
                    "credential_preview": cred_preview,
                    "filter": {"indy": {"cred_def_id": cred_def_id}},
                    "trace": exchange_tracing,
                }
                return offer_request

            elif cred_type == CRED_FORMAT_JSON_LD:
                offer_request = {
                    "connection_id": self.connection_id,
                    "filter": {
                        "ld_proof": {
                            "credential": {
                                "@context": [
                                    "https://www.w3.org/2018/credentials/v1",
                                    "https://w3id.org/citizenship/v1",
                                    "https://w3id.org/security/bbs/v1",
                                ],
                                "type": [
                                    "VerifiableCredential",
                                    "PermanentResident",
                                ],
                                "id": "https://credential.example.com/residents/1234567890",
                                "issuer": self.did,
                                "issuanceDate": "2020-01-01T12:00:00Z",
                                "credentialSubject": {
                                    "type": ["PermanentResident"],
                                    "givenName": "ALICE",
                                    "familyName": "SMITH",
                                    "gender": "Female",
                                    "birthCountry": "Bahamas",
                                    "birthDate": "1958-07-17",
                                },
                            },
                            "options": {"proofType": SIG_TYPE_BLS},
                        }
                    },
                }
                return offer_request

            else:
                raise Exception(f"Error invalid credential type: {self.cred_type}")

        else:
            raise Exception(f"Error invalid AIP level: {self.aip}")

    def generate_proof_request_web_request(
        self, aip, cred_type, revocation, exchange_tracing, connectionless=False
    ):
        print(aip, cred_type, self.connection_id)

        age = 1
        d = datetime.date.today()
        enrollDate = datetime.date(d.year - age, d.month, d.day)
        enrollDate_format = "%Y%m%d"
        if aip == 10:
            req_attrs = [
                {
                    "name": "enrollDate",
                    "restrictions": [{"schema_name": "oem_schema"}],
                },
                {
                    "name": "type",
                    "restrictions": [{"schema_name": "oem_schema"}],
                },
            ]
            if revocation:
                req_attrs.append(
                    {
                        "name": "type",
                        "restrictions": [{"schema_name": "oem_schema"}],
                        "non_revoked": {"to": int(time.time() - 1)},
                    },
                )
            else:
                req_attrs.append(
                    {
                        "name": "type",
                        "restrictions": [{"schema_name": "oem_schema"}],
                    }
                )
            if SELF_ATTESTED:
                # test self-attested claims
                req_attrs.append(
                    {"name": "self_attested_thing"},
                )
            """
            req_preds = [
                # test zero-knowledge proofs
                {
                    "name": "enrollDate",
                    "p_type": "<=",
                    "p_value": int(enrollDate.strftime(enrollDate_format)),
                    "restrictions": [{"schema_name": "oem_schema"}],
                }
            ]"""
            indy_proof_request = {
                "name": "Proof of Education",
                "version": "1.0",
                "requested_attributes": {
                    f"0_{req_attr['name']}_uuid": req_attr for req_attr in req_attrs
                },
                #"requested_predicates": {
                #    f"0_{req_pred['name']}_GE_uuid": req_pred for req_pred in req_preds
                #},
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
                        "name": "name",
                        "restrictions": [{"schema_name": "oem_schema"}],
                    },
                    {
                        "name": "type",
                        "restrictions": [{"schema_name": "oem_schema"}],
                    },
                ]
                if revocation:
                    req_attrs.append(
                        {
                            "name": "type",
                            "restrictions": [{"schema_name": "oem_schema"}],
                            "non_revoked": {"to": int(time.time() - 1)},
                        },
                    )
                else:
                    req_attrs.append(
                        {
                            "name": "type",
                            "restrictions": [{"schema_name": "oem_schema"}],
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
                        "name": "enrollDate",
                        "p_type": "<=",
                        "p_value": int(enrollDate.strftime(enrollDate_format)),
                        "restrictions": [{"schema_name": "oem_schema"}],
                    }
                ]
                indy_proof_request = {
                    "name": "Proof of Education",
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


async def main(args):
    consortium_agent = await create_agent_with_args(args, ident="consortium")

    async def check_for_new_connection(n):
        response = await consortium_agent.agent.admin_GET(f"/connections")
        n_results = len(response["results"])
        if n < n_results:
            n += 1
            print("New Connection")
            last_result = response["results"][-1]  # get the last element of the 'results' array
            time.sleep(3)
            consortium_agent.agent.connection_id = last_result["connection_id"]  # get the value of the 'connection_id' field
            offer_request = consortium_agent.agent.generate_credential_offer(
                consortium_agent.aip,
                consortium_agent.cred_type,
                consortium_agent.cred_def_id,
                exchange_tracing,
            )
            #issue Consorcium enrollment VC
            await consortium_agent.agent.admin_POST(
                "/issue-credential-2.0/send-offer", offer_request
            )
            #
            #command = 'peer chaincode query -C mychannel -n basic -c \'{"Args":["GetAllAssets"]}\''
            #result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
            #print(result.stdout.decode('utf-8'))


        return n  # always return the value of n


    try:
        log_status(
            "#1 Provision an agent and wallet, get back configuration details"
            + (
                f" (Wallet type: {consortium_agent.wallet_type})"
                if consortium_agent.wallet_type
                else ""
            )
        )
        agent = ConsortiumAgent(
            "consortium.agent",
            consortium_agent.start_port,
            consortium_agent.start_port + 1,
            genesis_data=consortium_agent.genesis_txns,
            genesis_txn_list=consortium_agent.genesis_txn_list,
            no_auto=consortium_agent.no_auto,
            tails_server_base_url=consortium_agent.tails_server_base_url,
            revocation=consortium_agent.revocation,
            timing=consortium_agent.show_timing,
            multitenant=consortium_agent.multitenant,
            mediation=consortium_agent.mediation,
            wallet_type=consortium_agent.wallet_type,
            seed=consortium_agent.seed,
            aip=consortium_agent.aip,
            endorser_role=consortium_agent.endorser_role,
        )

        consortium_schema_name = "Enrollment_VC"
        consortium_schema_attrs = [
            "name",
            "type",
            "enrollDate",
            "timestamp",
        ]
        if consortium_agent.cred_type == CRED_FORMAT_INDY:
            consortium_agent.public_did = True
            await consortium_agent.initialize(
                the_agent=agent,
                schema_name=consortium_schema_name,
                schema_attrs=consortium_schema_attrs,
                create_endorser_agent=(consortium_agent.endorser_role == "author")
                if consortium_agent.endorser_role
                else False,
            )
        elif consortium_agent.cred_type == CRED_FORMAT_JSON_LD:
            consortium_agent.public_did = True
            await consortium_agent.initialize(the_agent=agent)
        else:
            raise Exception("Invalid credential type:" + consortium_agent.cred_type)


        #create SD and GW schema and credential def
        sd_gw_schema_name = "Genesis_VC"
        sd_gw_schema_attrs = [
            "name",
            "deviceID",
            "deviceModelID",
            "manufactureDate",
            "timestamp",
        ]
        consortium_agent.cred_def_id_sd_gw = await consortium_agent.create_schema_and_cred_def(
                sd_gw_schema_name, sd_gw_schema_attrs
            )
        
        #create SD and GW schema and credential def
        sd_gw_schema_name = "Ownership_VC"
        sd_gw_schema_attrs = [
            "deviceID",
            "deviceModelID",
            "aquisitionDate",
            "timestamp",
        ]
        consortium_agent.cred_def_id_sd_gw = await consortium_agent.create_schema_and_cred_def(
                sd_gw_schema_name, sd_gw_schema_attrs
            )

        exchange_tracing = False
        options = (
            "    (1)  Issue Credential to OEM\n"
            "    (2)  Send Proof Request\n"
 #           "    (2a) Send *Connectionless* Proof Request (requires a Mobile client)\n"
            "    (3)  Send Message\n"
            "    (3a) Get All Connections\n"
            "    (4)  Create New Invitation\n"
        )
        if consortium_agent.revocation:
            options += "    (5) Revoke Credential\n" "    (6) Publish Revocations\n"
        if consortium_agent.endorser_role and consortium_agent.endorser_role == "author":
            options += "    (D) Set Endorser's DID\n"
        if consortium_agent.multitenant:
            options += "    (W) Create and/or Enable Wallet\n"
   #     options += "    (T) Toggle tracing on credential/proof exchange\n"
        options += "    (X) Exit?\n[1/2/3/4/{}{}T/X] ".format(
            "5/6/" if consortium_agent.revocation else "",
            "W/" if consortium_agent.multitenant else "",
        )
        print("Ready to receive connections!")
        stop = False
        n_connections = 0
        #while stop != True:
        #    n_connections = await check_for_new_connection(n_connections)
        async for option in prompt_loop(options):
            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break          

        if consortium_agent.show_timing:
            timing = await consortium_agent.agent.fetch_timing()
            if timing:
                for line in consortium_agent.agent.format_timing(timing):
                    log_msg(line)

    finally:
        terminated = await consortium_agent.terminate()

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
