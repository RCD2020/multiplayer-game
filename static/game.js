// Robert Davis
// 2024.05.06

// dynamic url
var url = window.location.href;
url = url.slice(0, url.length - 7);

var socket = io.connect(url);

socket.on('connect', function() {
    socket.emit('connect');
});