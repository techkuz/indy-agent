(function(){

    const TOKEN = document.getElementById("ui_token").innerText;

    var sendInviteButton = document.getElementById("btn_send_invite");

    connectionsTable = document.getElementById("conns-new");

    const MESSAGE_TYPES = {
        STATE: "urn:sovrin:agent:message_type:sovrin.org/ui/state",
        STATE_REQUEST: "urn:sovrin:agent:message_type:sovrin.org/ui/state_request",
        INITIALIZE: "urn:sovrin:agent:message_type:sovrin.org/ui/initialize",

        UI: {
            SEND_INVITE: "urn:sovrin:agent:message_type:sovrin.org/ui/send_invite",
            INVITE_SENT: "urn:sovrin:agent:message_type:sovrin.org/ui/invite_sent",
            INVITE_RECEIVED: "urn:sovrin:agent:message_type:sovrin.org/ui/invite_received",

            SEND_REQUEST: "urn:sovrin:agent:message_type:sovrin.org/ui/send_request",
            REQUEST_SENT: "urn:sovrin:agent:message_type:sovrin.org/ui/request_sent",
            REQUEST_RECEIVED: "urn:sovrin:agent:message_type:sovrin.org/ui/request_received",

            FTK_RECEIVED: "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/routing/1.0/forward_to_key",

            SEND_RESPONSE: "urn:sovrin:agent:message_type:sovrin.org/ui/send_response",
            RESPONSE_SENT: "urn:sovrin:agent:message_type:sovrin.org/ui/response_sent"
        },
        CONN: {

        }
    };

    // var message_display = $('#message_display');

    // Message Router {{{
    var msg_router = {
        routes: [],
        route:
            function(socket, msg) {
                if (msg.type in this.routes) {
                    this.routes[msg.type](socket, msg);
                } else {
                    console.log('Message from server without registered route: ' + JSON.stringify(msg));
                }
            },
        register:
            function(msg_type, fn) {
                this.routes[msg_type] = fn
            }
    };
    // }}}

    // UI Agent {{{
    var ui_agent = {
        connect:
        function (socket) {
            socket.send(JSON.stringify(
                {
                    type: MESSAGE_TYPES.STATE_REQUEST,
                    id: TOKEN,
                    message: null
                }
            ));
        },
        update:
        function (socket, msg) {
            state = msg.message;
            if (state.initialized === false) {
                showTab('login');
            } else {
                document.getElementById('agent_name').value = state.agent_name;
                document.getElementById('agent_name_header').innerHTML = "Agent's name: " + state.agent_name;
                showTab('relationships');
            }
        },
        inititialize:
        function (socket) {
            init_message = {
                type: MESSAGE_TYPES.INITIALIZE,
                id: TOKEN,
                message: {
                    name: document.getElementById('agent_name').value,
                    passphrase: document.getElementById('passphrase').value
                }
            };
            socket.send(JSON.stringify(init_message));
        },
    };
    // }}}


    // Connections {{{
    var connections = {
        send_invite:
        function (socket) {
            msg = {
                type: MESSAGE_TYPES.UI.SEND_INVITE,
                id: TOKEN,
                message: {
                    name: document.getElementById('send_name').value,
                    endpoint: document.getElementById('send_endpoint').value
                }
            };
            socket.send(JSON.stringify(msg));

        },

        invite_sent:
        function (socket, msg) {
            displayConnection(msg.message.name, msg.message.id, [], 'Invite sent');
        },

        invite_received:
        function (socket, msg) {
            displayConnection(msg.message.name, msg.message.id, [['Send Request', connections.send_request, socket, msg]], 'Invite received');
        },

        send_request:
        function (socket, prevMsg) {
            msg = {
                type: MESSAGE_TYPES.UI.SEND_REQUEST,
                id: TOKEN,
                message: {
                        name: prevMsg.message.name,
                        endpoint: prevMsg.message.endpoint.url,
                        key: prevMsg.message.endpoint.verkey,
                }
            };
            socket.send(JSON.stringify(msg));

        },

        request_sent:
        function (socket, msg) {
            displayConnection(msg.message.name, msg.message.id, [], 'Request sent');
        },

        ftk_received:
        function (socket, msg) {
            displayConnection(msg.message.name, msg.message.id, [['Send response', connections.send_response, socket, msg]], 'Request received');
        },

        send_response:
        function (socket, msg) {
            msg = {
                type: MESSAGE_TYPES.UI.SEND_RESPONSE,
                id: TOKEN,
                message: {
                        name: msg.message.name,
                        endpoint_key: msg.message.endpoint_key,
                        endpoint_uri: msg.message.endpoint_uri,
                }
            };

            socket.send(JSON.stringify(msg));
        },

        response_sent:
        function (socket, msg) {
            displayConnection(msg.message.name, msg.message.id, [], 'Response sent');
        }

    };
    // }}}

    // Message Routes {{{
    msg_router.register(MESSAGE_TYPES.STATE, ui_agent.update);


    msg_router.register(MESSAGE_TYPES.UI.INVITE_SENT, connections.invite_sent);
    msg_router.register(MESSAGE_TYPES.UI.INVITE_RECEIVED, connections.invite_received);
    msg_router.register(MESSAGE_TYPES.UI.REQUEST_SENT, connections.request_sent);
    // msg_router.register(MESSAGE_TYPES.UI.REQUEST_RECEIVED, connections.request_received);
    msg_router.register(MESSAGE_TYPES.UI.FTK_RECEIVED, connections.ftk_received);
    msg_router.register(MESSAGE_TYPES.UI.RESPONSE_SENT, connections.response_sent);




    // }}}

    // Create WebSocket connection.
    const socket = new WebSocket('ws://' + window.location.hostname + ':' + window.location.port + '/ws');

    // Connection opened
    socket.addEventListener('open', function(event) {
        ui_agent.connect(socket);
    });

    // Listen for messages
    socket.addEventListener('message', function (event) {
        console.log('Routing: ' + event.data);
        msg = JSON.parse(event.data);
        msg_router.route(socket, msg);
    });

    // DOM Event Listeners {{{
    // Need reference to socket so must be after socket creation
    document.getElementById('send_offer').addEventListener(
        "click",
        function (event) { connections.send_invite(socket); }
    );

    document.getElementById('agent_init').addEventListener(
        "click",
        function (event) {
            ui_agent.inititialize(socket);
            sendInviteButton.style.display = "block";
        }
    );

    function displayConnection(connName, connId, actions, status) {
        let row = connectionsTable.insertRow();
        row.id = connName + "_row";
        let cell1 = row.insertCell();
        let cell2 = row.insertCell();
        let cell3 = row.insertCell();
        let cell4 = row.insertCell();
        let cell5 = row.insertCell();

        let history_btn = document.createElement("button");
        history_btn.id = connName + "_history";
        history_btn.type = "button";
        history_btn.className = "btn btn-info";
        history_btn.textContent = "View";
        history_btn.setAttribute('data-toggle', 'modal');
        history_btn.setAttribute('data-target', '#exampleModal');

        history_btn.addEventListener(
            "click",
            function (event) {
                if(status === "Connected") {
                    document.getElementById("history_body").innerText = conns[connId].join('');
                }
                else if(status === "Pending") {
                    document.getElementById("history_body").innerText = pending_conns[connId].join('');
                }
                else if(status === "Received") {
                    document.getElementById("history_body").innerText = received_conns[connId].join('');
                }

            }
        );

        actions.forEach(function (item, i, actions) {
            let butn = document.createElement("button");
            butn.id = connName + "_" + item[0];
            butn.type = "button";
            butn.className = "btn btn-warning   ";
            butn.textContent = item[0];
            butn.addEventListener(
                "click",
                function (event) {
                     item[1](item[2], item[3]);
                }
            );
            cell5.appendChild(butn);

        });

        cell1.innerHTML = "#";
        cell2.innerHTML = connName;
        cell3.innerHTML = status;
        cell4.appendChild(history_btn);
    }

    // }}}

})();
