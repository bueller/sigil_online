

function main() {
  var socket = new WebSocket("ws://" + location.host + "/api/game");
  socket.onmessage = function (event) {
    alert(event.data);
  };
}
