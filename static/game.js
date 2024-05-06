// Robert Davis
// 2024.05.06

// dynamic url
var url = window.location.href;
var game_id = url.slice(-6);
url = url.slice(0, url.length - 12);

var socket = io.connect(url);

socket.on('connect', function() {
    socket.emit('connect_server', game_id);
});

// socket.on('disconnect', function() {
//     socket.emit('disconnect_server');
// });