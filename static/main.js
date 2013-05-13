var socket = io.connect();

// page refreshed, need to keep sockets up to date
function reconnect(nickname, pw) {
    socket.emit('reconnect', nickname, pw);
}
