// Robert Davis
// 2024.05.04

var url = window.location.href;
url = url.slice(0, url.length - 5);

var socket = io.connect(url);
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