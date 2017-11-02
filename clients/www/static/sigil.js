function chatEvent(event) {
  var payload = JSON.parse(event.data);
  document.getElementById('chatBox').innerHTML += '<br /><b>Player ' + payload.player + '</b>: ' + payload.message;
  return false;
}

function main() {
  events = new WebSocket("ws://" + location.host + "/api/game");
  events.onmessage = function (event) {
    alert(event.data);
    return false;
  };
  chat = new WebSocket("ws://" + location.host + "/api/chat");
  chat.onmessage = chatEvent;
}

function chatInputKeypress(e) {
  e = e || window.event;
  if (e.keyCode == 13) {
    var message = document.getElementById('chatInput').value;
    var payload = {"message": message};
    chat.send(JSON.stringify(payload));
    document.getElementById('chatInput').value = '';
  }
}
