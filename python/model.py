""" Data Model Classes.
"""

# Generally, in Python, classes are not intended to be used for data alone.
# These types of classes usually fit better as a dictionary. Here, however,
# we use classes to formalize the data being stored in these objects.

# pylint: disable=too-few-public-methods
import asyncio

from helpers import deserialize_bytes_json, serialize_bytes_json
from indy import did, crypto


class Agent:
    """ Data Model for all information needed for agent operation.
    """

    def __init__(self):
        self.owner = None
        self.wallet_handle = None
        self.endpoint = None
        self.endpoint_vk = None
        self.ui_token = None
        self.pool_handle = None
        self.connections = {}
        self.ui_socket = None
        self.initialized = False
        self.pending_offers = {}
        self.received_offers = {}


class Message(object):
    """ Data Model for messages.
    """

    def __init__(self, type, id, message):
        """ Create a Message object

            type: string denoting the message type. Standardization efforts are in progress.
            id: identifier for message. Usually a nonce or a DID. This combined with the type
                tell us how to interpret the message.
            message: ambiguous data. Interpretation defined by type and id.

        """
        self.type = type
        self.id = id
        self.message = message


class NewMessage(object):
    def __init__(self, *args, **kwargs):
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

    async def auth_crypt_content(self, wallet_handle, sender_vk, recipient_vk, msg):
        self.content = await crypto.auth_crypt(wallet_handle, sender_vk, recipient_vk, msg)

    def auth_decrypt_content(self):
        pass

    def anon_crypt_content(self):
        pass

    def anon_decrypt_content(self):
        pass

    def to_json(self):
        pass

    def to_bytes(self):
        pass
