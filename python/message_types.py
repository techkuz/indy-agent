""" Message Type Definitions, organized by class
"""


class CONN:
    """ Connetion Class of Message Types.

        This type notation is still being discussed and may change.
    """

class UI:
    STATE = "urn:sovrin:agent:message_type:sovrin.org/ui/state"
    STATE_REQUEST = "urn:sovrin:agent:message_type:sovrin.org/ui/state_request"
    INITIALIZE = "urn:sovrin:agent:message_type:sovrin.org/ui/initialize"


class UI_NEW:
    SEND_INVITE = "urn:sovrin:agent:message_type:sovrin.org/ui/send_invite"
    INVITE_SENT = "urn:sovrin:agent:message_type:sovrin.org/ui/invite_sent"
    INVITE_RECEIVED = "urn:sovrin:agent:message_type:sovrin.org/ui/invite_received"

    SEND_REQUEST = "urn:sovrin:agent:message_type:sovrin.org/ui/send_request"
    REQUEST_SENT = "urn:sovrin:agent:message_type:sovrin.org/ui/request_sent"
    REQUEST_RECEIVED = "urn:sovrin:agent:message_type:sovrin.org/ui/request_received"
    FTK_RECEIVED = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/routing/1.0/forward_to_key"

    SEND_RESPONSE = "urn:sovrin:agent:message_type:sovrin.org/ui/send_response"
    RESPONSE_SENT = "urn:sovrin:agent:message_type:sovrin.org/ui/response_sent"


class CONN_NEW:
    SEND_INVITE = "urn:sovrin:agent:message_type:sovrin.org/connection/send_invite"
    SEND_REQUEST = "urn:sovrin:agent:message_type:sovrin.org/connection/send_request"
    FORWARD_TO_KEY = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/routing/1.0/forward_to_key"
    FORWARD = "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/routing/1.0/forward"

