import base64
import json
import asyncio

from indy import crypto, wallet, did


async def agent_setup(name):
    wallet_config = json.dumps({"id": name + "_wallet"})
    wallet_credentials = json.dumps({"key": name + "_wallet_key"})

    try:
        await wallet.create_wallet(wallet_config, wallet_credentials)
    except Exception as e:
        await wallet.delete_wallet(wallet_config, wallet_credentials)
        await wallet.create_wallet(wallet_config, wallet_credentials)

    try:
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
    except Exception as e:
        print(e)
        print("Could not open wallet!")

    (endpoint_did, endpoint_key) = await did.create_and_store_my_did(wallet_handle, "{}")

    return wallet_handle, endpoint_did, endpoint_key


async def main(a_values, b_values):
    a_wallet_handle, a_endpoint_did, a_endpoint_key = a_values
    print('Agent a values are: ', a_values)
    b_wallet_handle, b_endpoint_did, b_endpoint_key = b_values
    print('Agent b values are: ', b_values)


    b_endpoint_did_str = b_endpoint_did
    msg_to_pass_bytes = str.encode(b_endpoint_did_str)
    content_encrypted = await crypto.auth_crypt(b_wallet_handle, b_endpoint_key, a_endpoint_key, msg_to_pass_bytes) # we have to pass bytes type exactly as msg
    content_decrypted_key, content_decrypted_bytes = await crypto.auth_decrypt(a_wallet_handle, a_endpoint_key, content_encrypted)
    content_decrypted_str = content_decrypted_bytes.decode('utf-8')
    assert b_endpoint_did_str == content_decrypted_str
    assert content_decrypted_key == b_endpoint_key

    b64_encrypted = base64.b64encode(content_encrypted)
    b64_decrypted = base64.b64decode(b64_encrypted)
    assert b64_decrypted == content_encrypted

    b64_encrypted_str = b64_encrypted.decode('utf-8')
    b64_encrypted_str_bytes = b64_encrypted_str.encode('utf-8')
    assert b64_encrypted_str_bytes == b64_encrypted

    inner_msg = json.dumps(
        {
            'type': 'did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/routing/1.0/forward_to_key',
            'key': b_endpoint_key,
            'content':
                {
                    'type': "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/request",
                    'key': b_endpoint_key,
                    'content': b64_encrypted_str
                }
        }
    )

    inner_msg_bytes = str.encode(inner_msg)
    inner_msg_encrypted = await crypto.anon_crypt(a_endpoint_key, inner_msg_bytes)
    inner_msg_decrypted_bytes = await crypto.anon_decrypt(a_wallet_handle, a_endpoint_key, inner_msg_encrypted)
    inner_msg_decrypted_str = inner_msg_decrypted_bytes.decode('utf-8')
    assert inner_msg == inner_msg_decrypted_str

    inner_msg = json.dumps(
        {
            'type': 'did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/routing/1.0/forward_to_key',
            'key': b_endpoint_key,
            'content':
                {
                    'type': "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/request",
                    'key': b_endpoint_key,
                    'content': base64.b64encode(await crypto.auth_crypt(b_wallet_handle, b_endpoint_key, a_endpoint_key, str.encode(b_endpoint_did))).decode('utf-8')
                }
        }
    )

    print('Inner message is: ', inner_msg)

    outer_message = json.dumps(
        {
            'content': base64.b64encode(await crypto.anon_crypt(a_endpoint_key, str.encode(inner_msg))).decode('utf-8')
        }
    )

    print('Outer message is: ', outer_message)

    message = json.loads(outer_message)
    print(1, message)
    content = message['content']
    print(2, content)
    content_as_bytes = content.encode('utf-8')
    print(3, content_as_bytes)
    ciphertext = base64.b64decode(content_as_bytes)
    print(4, ciphertext)
    decrypted_inner_msg = (await crypto.anon_decrypt(a_wallet_handle, a_endpoint_key,ciphertext)).decode('utf-8')
    print(5, decrypted_inner_msg)
    print(len(decrypted_inner_msg))

    inner_msg_as_dict = json.loads(decrypted_inner_msg)
    print(6, inner_msg_as_dict)
    inner_msg_content = inner_msg_as_dict['content']
    print(7, inner_msg_content)
    inside_inner_msg_content = inner_msg_content['content']
    print(8, inside_inner_msg_content)
    iimc_as_bytes = inside_inner_msg_content.encode('utf-8')
    print(9, iimc_as_bytes)
    inner_ciphertext = base64.b64decode(iimc_as_bytes)
    print(inner_ciphertext, '\n', 'end')
    # bobs_endpoint_did_as_bytes = crypto.auth_decrypt()
    #
    # message = json.loads(outer_message['content']).encode('utf-8')
    # print('Encoded utf-8 message is: ', message)
    #
    # message = base64.urlsafe_b64decode(message)
    # print('Decoded base64 message is: ', message)
    #
    # decrypted_data = await crypto.anon_decrypt(a_wallet_handle, a_endpoint_key, message)
    # print('Decrypted data: ', decrypted_data)
    #
    # json_str = decrypted_data.decode()  # here we loose nested json of content inside inner_msg
    # print('Json str: ', json_str)
    #
    # resp_data = json.loads(json_str)  # json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
    #
    # print('Resp data: ', resp_data)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    a_values = loop.run_until_complete(agent_setup('alice'))
    b_values = loop.run_until_complete(agent_setup('bob'))
    loop.run_until_complete(main(a_values, b_values))
