from behave import given, when, then
from aries_cloudagent.messaging.request_context import RequestContext
from aries_cloudagent.messaging.agent_message import AgentMessage
from aries_cloudagent.messaging.agent_message import AgentMessage, AgentMessageSchema
from aries_cloudagent.messaging.responder import BaseResponder
from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.wallet.base import BaseWallet
from aries_cloudagent.ledger.base import BaseLedger
import asyncio
from aries_cloudagent.wallet.crypto import create_keypair
from aiohttp import web
from aries_cloudagent.messaging.outbound_message import OutboundMessage
from aries_cloudagent.storage.basic import BasicStorage
from aries_cloudagent.storage.record import StorageRecord
from aries_cloudagent.protocols.issue_credential.v1_0.models.credential_exchange import CredentialExchange
from aries_cloudagent.config.injection_context import InjectionContext
import Agent
from aiohttp import ClientSession


wallet = BaseWallet(...)
responder = BaseResponder(...)
storage = BaseStorage(...)
ledger = BaseLedger(...)


@given("Dave is on the consortium's marketing website")
def step_given_dave_on_marketing_website(context):
    # no code needed for this step
    pass


@when("Dave taps the 'Enroll OEM' button")
def step_when_dave_taps_enroll_button(context):
    async def request_oob_uri():
        request = {
            "@type": "admin-api/request_oob_uri",
            "some_parameter": "some_value"
        }
        agent_instance = context.agent_instance 
        response = await agent_instance.admin_api.process(request)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(request_oob_uri())


@then("the marketing website makes a call to C:1 Admin API to request an OOB URI")
def step_then_marketing_website_makes_api_call(context):
    async def make_api_call():
        api_url = "http://c1-admin-api.com/oob_uri"
        
        async with ClientSession() as session:
            response = await session.get(api_url)
            response_json = await response.json()
            oob_uri = response_json["oob_uri"]
            context.oob_uri = oob_uri  
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(make_api_call())

@when("the OEM staff deploys the DIDComm Agent")
def step_when_oem_staff_deploys_agent(context):
    async def deploy_didcomm_agent():
        config = {
            "wallet.type": "indy",
            "wallet.name": "oem_wallet",
            "wallet.key": "oem_wallet_key",
        }
        context = InjectionContext(enforce_typing=False)
        agent = Agent(context=context, config=config)
        
        await agent.start()

        await agent.join()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(deploy_didcomm_agent())


@then("O:1 creates its public DID during first boot")
def step_then_o1_creates_public_did(context):
    async def create_public_did():
        wallet = context.wallet 
        
        keypair = create_keypair()
        
        did_info, _ = await wallet.create_local_did(
            did=None, metadata=None, key_type=keypair["type"], seed=keypair["seed"]
        )
        
        public_did = did_info.did
        context.public_did = public_did
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_public_did())


@when("D:1 clicks the OOB URI")
def step_when_d1_clicks_oob_uri(context):
    async def handle_oob_uri():
        oob_uri = context.oob_uri 
        app = web.Application()
        app.router.add_get("/")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", 8080)
        await site.start()
        
        await asyncio.Event().wait()


@then("D:1 establishes a connection with C:1 using the OOB URI")
def step_then_d1_establishes_connection_with_c1(context):
    async def establish_connection():
        oob_uri = context.oob_uri 
        connection_request = {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/request",
            "connection": {
                "invitation": oob_uri
            }
        }
        
        message = OutboundMessage(payload=connection_request)
        responder = context.responder  
        
        await responder.send_outbound(message)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(establish_connection())


@then("C:1 creates a new entry into the Agent Table")
def step_then_c1_creates_entry_in_agent_table(context):
    async def create_agent_entry():
        agent_table = context.agent_table  
        wallet = context.wallet  
        
        record = StorageRecord(
            type_=CredentialExchange.RECORD_TYPE,
            value={
                "connection_id": context.connection_id,
                "oem_enrollment_id": context.oem_enrollment_id
            }
        )
        
        storage = BasicStorage(wallet)
        await storage.add_record(agent_table, record)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_agent_entry())


@when("D:1 establishes a connection with O:1 using an implicit invitation")
def step_when_d1_establishes_connection_with_o1(context):
    async def establish_connection():
        implicit_invitation = context.implicit_invitation
        
        invitation_message = AgentMessage.deserialize(implicit_invitation)
        
        message = OutboundMessage(payload=invitation_message)
        responder = context.responder  
        
        await responder.send_outbound(message)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(establish_connection())