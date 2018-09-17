""" Module to handle the connection process.
"""

# pylint: disable=import-error

import json
import base64
import aiohttp
from indy import crypto, did

import serializer.json_serializer as Serializer
from model import Message
from message_types import UI_NEW, CONN_NEW
from helpers import serialize_bytes_json, bytes_to_str, str_to_bytes


async def send_invite(msg, agent):
    receiver_endpoint = msg.message['endpoint']
    conn_name = msg.message['name']

    (endpoint_did, endpoint_key) = await did.create_and_store_my_did(agent.wallet_handle, "{}")
    agent.verkey = endpoint_key

    msg = Message(
        CONN_NEW.SEND_INVITE,
        0,
        {
            'name': conn_name,
            'endpoint': {
                'url': agent.endpoint,
                'verkey': endpoint_key,
            },
        }
    )
    serialized_msg = Serializer.pack(msg)
    async with aiohttp.ClientSession() as session:
        async with session.post(receiver_endpoint, data=serialized_msg) as resp:
            print(resp.status)
            print(await resp.text())

    return Message(UI_NEW.INVITE_SENT, agent.ui_token, {'name': conn_name, 'id': 0})


async def invite_received(msg, agent):
    conn_name = msg.message['name']

    invite_received_msg = Message(
        UI_NEW.INVITE_RECEIVED,
        0,
        {'name': conn_name,
         'endpoint': msg.message['endpoint']}
    )

    return invite_received_msg


async def send_request(msg, agent):
    endpoint = msg.message['endpoint']
    name = msg.message['name']
    connection_key = msg.message['key']

    my_endpoint_uri = agent.endpoint

    (endpoint_did_int, endpoint_key) = await did.create_and_store_my_did(agent.wallet_handle, "{}")

    agent.verkey = endpoint_key

    endpoint_did_bytes = str_to_bytes(endpoint_did_int)

    agent.did_bytes = endpoint_did_bytes

    inner_msg = json.dumps(
        {
            'type': 'did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/routing/1.0/forward_to_key',
            'id': agent.verkey,
            'message': json.dumps(
                {
                    'type': "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/request",
                    'id': agent.verkey,
                    'endpoint': my_endpoint_uri,
                    'message': serialize_bytes_json(await crypto.auth_crypt(agent.wallet_handle, agent.verkey, connection_key, endpoint_did_bytes))
                }
            )
        }
    )

    inner_msg_bytes = str_to_bytes(inner_msg)

    outer_message = json.dumps(
        {
            'type': CONN_NEW.SEND_REQUEST,
            'id': 0,
            'message': serialize_bytes_json(await crypto.anon_crypt(connection_key, inner_msg_bytes))
        }
    )

    # serialized_msg = Serializer.unpack(outer_message)
    # print(serialized_msg, 'send')
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, data=outer_message) as resp:
            print(resp.status)
            print(await resp.text())

    return Message(UI_NEW.REQUEST_SENT, agent.ui_token, {'name': name, 'id': 0})


async def ftk_received(msg, agent):
    print('ftk')
    inner_msg_str = msg.message
    inner_msg_json = json.loads(inner_msg_str)

    sender_endpoint_uri = inner_msg_json['endpoint']
    endpoint_key = inner_msg_json['id']

    message_bytes = inner_msg_json['message'].encode('utf-8')
    message_bytes = base64.b64decode(message_bytes)

    sender_key_str, sender_did_bytes = await crypto.auth_decrypt(agent.wallet_handle, agent.verkey, message_bytes)
    sender_did_str = sender_did_bytes.decode('utf-8')

    ftk_received_msg = Message(
        UI_NEW.FTK_RECEIVED,
        0,
        {'name': 0,
         'endpoint_uri': sender_endpoint_uri,
         'endpoint_key': endpoint_key,
         'did': sender_did_str} # what to do with it?
    )

    return ftk_received_msg


async def send_response(msg, agent):
    print('response')
    receiver_endpoint_uri = msg.message['endpoint_uri']
    receiver_endpoint_key = msg.message['endpoint_key']

    inner_msg = json.dumps(
        {
            'type': "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/response",
            'to': "did:sov:ABC",
            'id': 0,
            'message': serialize_bytes_json(await crypto.auth_crypt(agent.wallet_handle, agent.verkey, receiver_endpoint_key, agent.did_bytes))
        }
    )
    print(5)
    outer_msg = json.dumps({
        'type': "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/routing/1.0/forward",
        'to': "ABC",
        'id': 0,
        'message': inner_msg
    })

    outer_msg_bytes = str_to_bytes(outer_msg)

    all_message = json.dumps({
        'type': 0,
        'id': 0,
        'message': serialize_bytes_json(await crypto.anon_crypt(receiver_endpoint_key, outer_msg_bytes))
    })

    async with aiohttp.ClientSession() as session:
        async with session.post(receiver_endpoint_uri, data=all_message) as resp:
            print(resp.status)
            print(await resp.text())

    return Message(UI_NEW.RESPONSE_SENT, agent.ui_token, {'name': 0, 'id': 0})


async def forward_received(msg, agent):
    print('forward')
    inner_msg_str = msg.message
    inner_msg_json = json.loads(inner_msg_str)

    sender_endpoint_uri = inner_msg_json['endpoint']
    endpoint_key = inner_msg_json['id']

    message_bytes = inner_msg_json['message'].encode('utf-8')
    message_bytes = base64.b64decode(message_bytes)

    sender_key_str, sender_did_bytes = await crypto.auth_decrypt(agent.wallet_handle, agent.verkey, message_bytes)
    sender_did_str = sender_did_bytes.decode('utf-8')

    forward_received_msg = Message(
        UI_NEW.FTK_RECEIVED,
        0,
        {'name': 0,
         'endpoint_uri': sender_endpoint_uri,
         'endpoint_key': endpoint_key,
         'did': sender_did_str}
    )

    return forward_received_msg

