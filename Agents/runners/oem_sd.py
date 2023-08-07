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
import subprocess
import uuid
import time


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
    CONS_PUB_DID,
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
GREEN = '\033[32m'
RESET = '\033[0m'

logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger(__name__)


class OEMAgent(AriesAgent):
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
            prefix="OEM_SD",
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

    def generate_gw_credential_offer(self, aip, cred_type, cred_def_id, exchange_tracing, uuid):
        print(cred_def_id)
        age = 0
        d = datetime.date.today()
        birth_date = datetime.date(d.year - age, d.month, d.day)
        birth_date_format = "%Y%m%d"
        if aip == 10:
            # define attributes to send for credential
            self.cred_attrs[cred_def_id] = {
                "name": "gatewayName",
                "model": "gatewayModel",
                "manufacture_date": birth_date.strftime(birth_date_format),
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
                    "name": "gatewayName",
                    "model": "gatewayModel",
                    "manufacture_date": birth_date.strftime(birth_date_format),
                    "timestamp": str(int(time.time())),
                    "deviceid": uuid
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

    def generate_sd_credential_offer(self, aip, cred_type, cred_def_id, exchange_tracing, uuid):
        age = 0
        d = datetime.date.today()
        birth_date = datetime.date(d.year - age, d.month, d.day)
        birth_date_format = "%Y%m%d"
        if aip == 10:
            # define attributes to send for credential
            self.cred_attrs[cred_def_id] = {
                "name": "gatewayName",
                "model": "gatewayModel",
                "manufacture_date": birth_date.strftime(birth_date_format),
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
                    "name": "smartDeviceName",
                    "model": "smartDeviceModel",
                    "manufacture_date": birth_date.strftime(birth_date_format),
                    "timestamp": str(int(time.time())),
                    "deviceid": uuid
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

    def generate_ownership_credential_offer(self, aip, cred_type, cred_def_id, exchange_tracing, uuid):
        age = 0
        d = datetime.date.today()
        birth_date = datetime.date(d.year - age, d.month, d.day)
        birth_date_format = "%Y%m%d"
        if aip == 10:
            # define attributes to send for credential
            self.cred_attrs[cred_def_id] = {
                "name": "gatewayName",
                "model": "gatewayModel",
                "manufacture_date": birth_date.strftime(birth_date_format),
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
                    "deviceUUID": uuid,
                    "model": "Model Specification",
                    "ownership_date": birth_date.strftime(birth_date_format),
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
                }
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
                    }
                ]
                indy_proof_request = {
                    "name": "Proof of GW/SD",
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
                }
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
    print(CONS_PUB_DID)
    
    total_start_time = time.time()
    oem_agent = await create_agent_with_args(args, ident="oem_sd")

    last_result = None
    async def check_for_new_connection(n, lr):
        response = await oem_agent.agent.admin_GET(f"/connections")
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
            oem_agent.agent.connection_id = last_result["connection_id"]  # get the value of the 'connection_id' field

        return n, last_result, response, newconnect   # always return the value of n
    
    async def check_for_new_message(lm, last_result):
        #time.sleep(1) # pause for 3 seconds
        #print("last m "+lm)
        #print("last o "+oem_agent.agent.lastmessage)
        #print("last r "+last_result)
        if lm != oem_agent.agent.lastmessage:
            #time.sleep(1)
            lm = oem_agent.agent.lastmessage
            #print(lm)
            #print(last_result)
            #uuid_obj = uuid.uuid4()
            #uuid_str = str(uuid_obj)
            #msg = uuid_str
            if last_result != None:
                oem_agent.agent.connection_id = last_result["connection_id"]  # get the value of the 'connection_id' field
                if "gateway" in last_result["their_label"]:
                    offer_request = oem_agent.agent.generate_gw_credential_offer(
                                oem_agent.aip,
                                oem_agent.cred_type,
                                oem_agent.cred_def_id,
                                False,
                                oem_agent.agent.lastmessage,
                            )
                elif "smartdevice" in last_result["their_label"]:
                    offer_request = oem_agent.agent.generate_sd_credential_offer(
                                oem_agent.aip,
                                oem_agent.cred_type,
                                oem_agent.cred_def_id,
                                False,
                                oem_agent.agent.lastmessage,
                            )
                else:
                    offer_request = oem_agent.agent.generate_ownership_credential_offer(
                                oem_agent.aip,
                                oem_agent.cred_type,
                                oem_agent.cred_def_id_ownership,
                                False,
                                oem_agent.agent.lastmessage,
                            )
                #await issue_cred(last_result, response)
                await oem_agent.agent.admin_POST(
                "/issue-credential-2.0/send-offer", offer_request)
            return lm
        return lm

    async def issue_cred(last_result, response):
        oem_agent.agent.connection_id = last_result["connection_id"]  # get the value of the 'connection_id' field
        print(response)
        print(oem_agent.agent.lastmessage)
        uuid = oem_agent.agent.lastmessage
        print(last_result["their_label"])

        if "gateway" in last_result["their_label"]:
            offer_request = oem_agent.agent.generate_gw_credential_offer(
                        oem_agent.aip,
                        oem_agent.cred_type,
                        oem_agent.cred_def_id,
                        False,
                        uuid,
                    )
        elif "smartdevice" in last_result["their_label"]:
            offer_request = oem_agent.agent.generate_sd_credential_offer(
                        oem_agent.aip,
                        oem_agent.cred_type,
                        oem_agent.cred_def_id,
                        False,
                        uuid,
                    )
        else:
            offer_request = oem_agent.agent.generate_ownership_credential_offer(
                        oem_agent.aip,
                        oem_agent.cred_type,
                        oem_agent.cred_def_id,
                        False,
                        uuid,
                    )
        

        #issue Consorcium enrollment VC
        await oem_agent.agent.admin_POST(
            "/issue-credential-2.0/send-offer", offer_request
        )
        
    try:
        log_status(
            "#1 Provision an agent and wallet, get back configuration details"
            + (
                f" (Wallet type: {oem_agent.wallet_type})"
                if oem_agent.wallet_type
                else ""
            )
        )
        agent = OEMAgent(
            "oem.sd.agent",
            oem_agent.start_port,
            oem_agent.start_port + 1,
            genesis_data=oem_agent.genesis_txns,
            genesis_txn_list=oem_agent.genesis_txn_list,
            no_auto=oem_agent.no_auto,
            tails_server_base_url=oem_agent.tails_server_base_url,
            revocation=oem_agent.revocation,
            timing=oem_agent.show_timing,
            multitenant=oem_agent.multitenant,
            mediation=oem_agent.mediation,
            wallet_type=oem_agent.wallet_type,
            seed=oem_agent.seed,
            aip=oem_agent.aip,
            endorser_role=oem_agent.endorser_role,
        )

        sd_gw_schema_name = "sd_gw_schema"
        sd_gw_schema_attrs = [
            "name",
            "model",
            "manufacture_date",
            "timestamp",
            "deviceid",
        ]
        if oem_agent.cred_type == CRED_FORMAT_INDY:
            oem_agent.public_did = True
            await oem_agent.initialize(
                the_agent=agent,
                #schema_name=sd_gw_schema_name,
                #schema_attrs=sd_gw_schema_attrs,
                create_endorser_agent=(oem_agent.endorser_role == "author")
                if oem_agent.endorser_role
                else False,
            )
        elif oem_agent.cred_type == CRED_FORMAT_JSON_LD:
            oem_agent.public_did = True
            await oem_agent.initialize(the_agent=agent)
        else:
            raise Exception("Invalid credential type:" + oem_agent.cred_type)

        #create SD and GW schema and credential def
        ownership_schema_name = "ownership_schema"
        ownership_schema_attrs = [
            "deviceUUID",
            "model",
            "ownership_date",
            "timestamp",
        ]
        #oem_agent.cred_def_id_ownership = await oem_agent.create_schema_and_cred_def_ownership(
        #        ownership_schema_name, ownership_schema_attrs
        #    )

        exchange_tracing = False
        options = (
            "    (1a) Issue GW Credential\n"
            "    (1b) Issue SD Credential\n"
            "    (1c) Issue Ownership Credential\n"
            "    (2) Send SD/GW Proof Request\n"
            "    (2c) Send Ownership Proof Request\n"
 #           "    (2a) Send *Connectionless* Proof Request (requires a Mobile client)\n"
            "    (3) Send Message\n"
            "    (3a) Get All Connections\n"
            "    (4a) Create New Invitation\n"
            "    (4b) Input New Invitation\n"
        )
        if oem_agent.revocation:
            options += "    (5) Revoke Credential\n" "    (6) Publish Revocations\n"
        if oem_agent.endorser_role and oem_agent.endorser_role == "author":
            options += "    (D) Set Endorser's DID\n"
        if oem_agent.multitenant:
            options += "    (W) Create and/or Enable Wallet\n"
#        options += "    (T) Toggle tracing on credential/proof exchange\n"
        options += "    (X) Exit?\n[1/2/3/4/{}{}T/X] ".format(
            "5/6/" if oem_agent.revocation else "",
            "W/" if oem_agent.multitenant else "",
        )

        print("Ready to receive connections!")
        stop = False
        n_connections = 1
        print(oem_agent.agent.lastmessage)
        last_message = "First"
        oem_agent.agent.lastmessage = ""
        while stop != True:
            n_connections, last_result, response, newconnect = await check_for_new_connection(n_connections, last_result)

            last_message = await check_for_new_message(last_message, last_result)

   
        if oem_agent.show_timing:
            timing = await oem_agent.agent.fetch_timing()
            if timing:
                for line in oem_agent.agent.format_timing(timing):
                    log_msg(line)

    finally:
        terminated = await oem_agent.terminate()

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
