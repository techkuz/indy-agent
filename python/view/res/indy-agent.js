(function(){

    const TOKEN = document.getElementById('ui_token').innerHTML;

    const MESSAGE_TYPES = {
        STATE: "urn:sovrin:agent:message_type:sovrin.org/ui/state",
        STATE_REQUEST: "urn:sovrin:agent:message_type:sovrin.org/ui/state_request",
        SEND_OFFER: "urn:sovrin:agent:message_type:sovrin.org/ui/send_offer",
        INITIALIZE: "urn:sovrin:agent:message_type:sovrin.org/ui/initialize",
        OFFER_RECEIVED: "urn:sovrin:agent:message_type:sovrin.org/ui/offer_received",
        OFFER_SENT: "urn:sovrin:agent:message_type:sovrin.org/ui/offer_sent",
        OFFER_ACCEPTED: "urn:sovrin:agent:message_type:sovrin.org/ui/offer_accepted",
        OFFER_REJECTED: "urn:sovrin:agent:message_type:sovrin.org/ui/offer_rejected",
    }

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
            state = msg.message
            if (state.initialized == false) {
                showTab('login');
            } else {
                document.getElementById('agent_name').value = state.agent_name;
                document.getElementById('agent_name_header').innerHTML = state.agent_name;
                conn_wrapper = document.getElementById('connections-wrapper');
                context = {'connections': state.connections};
                content = connections_template(context);
                conn_wrapper.innerHTML = content;
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

    function showTab(id) {
        let i;
        let x = document.getElementsByClassName("tab");
        for (i = 0; i < x.length; i++) {
            x[i].style.display = "none";
        }
        document.getElementById(id).style.display = "block";
    }

    // Connections {{{
    var connections = {
        send_offer:
        function (socket) {
            msg = {
                type: MESSAGE_TYPES.SEND_OFFER,
                id: TOKEN,
                message: {
                    name: document.getElementById('send_name').value,
                    endpoint: document.getElementById('send_endpoint').value
                }
            }
            socket.send(JSON.stringify(msg));
        },
        offer_sent:
        function (socket, msg) {
            context = {id: msg.id, name: msg.message.name, status: 'pending'};
            document.getElementById('connections-wrapper').innerHTML += connection_template(context);
            removeElementById(msg.message.name + '_accept');
            document.getElementById(msg.message.name + '_reject').addEventListener(
                "click",
                function (event) {
                     removeElementById(msg.message.name);
                     rej_msg = {
                        type: MESSAGE_TYPES.OFFER_REJECTED,
                        id: TOKEN,
                        message: {
                            name: msg.message.name
                        }
                     }
                     socket.send(JSON.stringify(rej_msg));
                }
            );

        },
        offer_recieved:
        function (socket, msg) {
            context = {name: msg.message.name, status: 'pending'};
            document.getElementById('connections-wrapper').innerHTML += connection_template(context);
            document.getElementById(msg.message.name + '_accept').addEventListener(
                "click",
                function (event) {
                    removeElementById(msg.message.name + '_accept');
                    acc_msg = {
                        type: MESSAGE_TYPES.OFFER_ACCEPTED,
                        id: TOKEN,
                        message: {
                        name: msg.message.name
                        }
                    }
                    socket.send(JSON.stringify(acc_msg));
                }
            );
            document.getElementById(msg.message.name + '_reject').addEventListener(
                "click",
                function (event) {
                     removeElementById(msg.message.name);
                     rej_msg = {
                        type: MESSAGE_TYPES.OFFER_REJECTED,
                        id: TOKEN,
                        message: {
                            name: msg.message.name
                        }
                     }
                     socket.send(JSON.stringify(rej_msg));
                }
            );
        },
    };
    // }}}

    // Templates {{{

    const connections_template = Handlebars.compile(document.getElementById('connections-template').innerHTML);
    const connection_template = Handlebars.compile(document.getElementById('connection-template').innerHTML);

    // }}}

    // Message Routes {{{
    msg_router.register(MESSAGE_TYPES.STATE, ui_agent.update);
    msg_router.register(MESSAGE_TYPES.OFFER_SENT, connections.offer_sent);
    msg_router.register(MESSAGE_TYPES.OFFER_RECEIVED, connections.offer_recieved);

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
        function (event) { connections.send_offer(socket); }
    );

    document.getElementById('agent_init').addEventListener(
        "click",
        function (event) { ui_agent.inititialize(socket); }
    );

    // }}}

})();
