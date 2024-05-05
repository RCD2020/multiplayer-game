var socket = io.connect('http://192.168.86.47:42069');
var messages = document.getElementById('messages');
var message_field = document.getElementById('message');
var submit_message = document.getElementById('submit_message');

socket.on('connect', function() {
    socket.emit('send_json');
});

socket.on('json_response', function(data) {
    console.log('Received JSON:', data);
});

socket.on('send_client', function(message) {
    var message_node = document.createElement('p');
    message_node.innerHTML = message['message'];
    messages.appendChild(message_node);
});

submit_message.onclick = function(){
    var text = message_field.value;
    if (text) {
        socket.emit('send_server', {'message': text});
    }
    message_field.value = '';
}