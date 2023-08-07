import asyncio
import base64
import binascii
import json
import logging
import os
import sys
from urllib.parse import urlparse
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runners.agent_container import (  # noqa:E402
    arg_parser,
    create_agent_with_args,
    AriesAgent,
)
from runners.support.utils import (  # noqa:E402
    check_requires,
    log_msg,
    log_status,
    log_timer,
    prompt,
    prompt_loop,
)


logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger(__name__)
GREEN = '\033[32m'
RESET = '\033[0m'

class CharlieAgent(AriesAgent):
    def __init__(
        self,
        ident: str,
        http_port: int,
        admin_port: int,
        no_auto: bool = False,
        aip: int = 20,
        endorser_role: str = None,
        **kwargs,
    ):
        super().__init__(
            ident,
            http_port,
            admin_port,
            prefix="Charlie",
            no_auto=no_auto,
            seed=None,
            aip=aip,
            endorser_role=endorser_role,
            **kwargs,
        )
        self.connection_id = None
        self._connection_ready = None
        self.cred_state = {}

    async def detect_connection(self):
        await self._connection_ready
        self._connection_ready = None

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()


async def input_invitation(agent_container):
    agent_container.agent._connection_ready = asyncio.Future()
    async for details in prompt_loop("Invite details: "):
        total_start_time = time.time()
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
    total_end_time = time.time()
    total_execution_time = total_end_time - total_start_time
    print(f"{GREEN}OOB URI connection: {total_execution_time} seconds{RESET}")


async def main(args):
    charlie_agent = await create_agent_with_args(args, ident="alice")

    try:
        log_status(
            "#7 Provision an agent and wallet, get back configuration details"
            + (
                f" (Wallet type: {charlie_agent.wallet_type})"
                if charlie_agent.wallet_type
                else ""
            )
        )
        agent = CharlieAgent(
            "charlie.agent",
            charlie_agent.start_port,
            charlie_agent.start_port + 1,
            genesis_data=charlie_agent.genesis_txns,
            genesis_txn_list=charlie_agent.genesis_txn_list,
            no_auto=charlie_agent.no_auto,
            tails_server_base_url=charlie_agent.tails_server_base_url,
            revocation=charlie_agent.revocation,
            timing=charlie_agent.show_timing,
            multitenant=charlie_agent.multitenant,
            mediation=charlie_agent.mediation,
            wallet_type=charlie_agent.wallet_type,
            aip=charlie_agent.aip,
            endorser_role=charlie_agent.endorser_role,
        )

        await charlie_agent.initialize(the_agent=agent)

        #log_status("#9 Input faber.py invitation details")
        #await input_invitation(charlie_agent)

        options = "    (3) Send Message\n" \
                "    (3a) Get All Connections\n" \
                "    (4) Input New Invitation\n" \
                "    (5) Buy Device\n" \
                "    (5a) Claim GW\n" \
                "    (5b) Claim SD\n" \
                "    (6a) Twin SD\n" \
                "    (6b) Untwin SD\n" \
                "    (7) Sell SD\n"
        if charlie_agent.endorser_role and charlie_agent.endorser_role == "author":
            options += "    (D) Set Endorser's DID\n"
        if charlie_agent.multitenant:
            options += "    (W) Create and/or Enable Wallet\n"
        options += "    (X) Exit?\n[3/4/{}X] ".format(
            "W/" if charlie_agent.multitenant else "",
        )
        async for option in prompt_loop(options):
            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break

            elif option in "dD" and charlie_agent.endorser_role:
                endorser_did = await prompt("Enter Endorser's DID: ")
                await charlie_agent.agent.admin_POST(
                    f"/transactions/{charlie_agent.agent.connection_id}/set-endorser-info",
                    params={"endorser_did": endorser_did, "endorser_name": "endorser"},
                )

            elif option in "wW" and charlie_agent.multitenant:
                target_wallet_name = await prompt("Enter wallet name: ")
                include_subwallet_webhook = await prompt(
                    "(Y/N) Create sub-wallet webhook target: "
                )
                if include_subwallet_webhook.lower() == "y":
                    await charlie_agent.agent.register_or_switch_wallet(
                        target_wallet_name,
                        webhook_port=charlie_agent.agent.get_new_webhook_port(),
                        mediator_agent=charlie_agent.mediator_agent,
                        taa_accept=charlie_agent.taa_accept,
                    )
                else:
                    await charlie_agent.agent.register_or_switch_wallet(
                        target_wallet_name,
                        mediator_agent=charlie_agent.mediator_agent,
                        taa_accept=charlie_agent.taa_accept,
                    )

            elif option == "3":
                msg = await prompt("Enter message: ")
                if msg:
                    await charlie_agent.agent.admin_POST(
                        f"/connections/{charlie_agent.agent.connection_id}/send-message",
                        {"content": msg},
                    )
            elif option == "3a":
                response = await charlie_agent.agent.admin_GET(f"/connections")
                print(response)
            elif option == "4":
                # handle new invitation
                log_status("Input new invitation details")
                await input_invitation(charlie_agent)
            elif option == "5":
                oempubdid = await prompt("Enter OEM PUB DID: ")
                devuuid = await prompt("Enter Device UUID: ")
                implicit_invitation = await charlie_agent.agent.admin_POST(f"/didexchange/create-request?their_public_did={oempubdid}&use_public_did=false")
                connectionid = implicit_invitation['connection_id']
                charlie_agent.agent.connection_id = connectionid
                time.sleep(1) 
                await charlie_agent.agent.admin_POST(
                    f"/connections/{charlie_agent.agent.connection_id}/send-message",
                    {"content": devuuid},
                )
            elif option == "5a":
                # handle new invitation
                log_status("Input GW QR Code")
                await input_invitation(charlie_agent)
            elif option == "5b":
                # handle new invitation
                log_status("Input GW QR Code to claim SD")
                await input_invitation(charlie_agent)
            elif option == "6a":
                # handle new invitation
                log_status("Input Twin Message")
                devuuid = await prompt("Enter Device UUID: ")
                data = await charlie_agent.agent.admin_GET(f"/connections")
                print(data)
                for connection in data['results']:
                    if connection['their_label'] == 'gateway.agent':
                        connection_id = connection['connection_id']
                        print(connection_id)
                await charlie_agent.agent.admin_POST(
                    f"/connections/{connection_id}/send-message",
                    {"content": devuuid},
                )

        if charlie_agent.show_timing:
            timing = await charlie_agent.agent.fetch_timing()
            if timing:
                for line in charlie_agent.agent.format_timing(timing):
                    log_msg(line)

    finally:
        terminated = await charlie_agent.terminate()

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    parser = arg_parser(ident="alice", port=8030)
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
                "Alice remote debugging to "
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

    check_requires(args)

    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
