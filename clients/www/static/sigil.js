

function main() {
  // awaiting is a global variable set to null when not awaiting anything,
  // set to 'node' when the server is awaiting a node name,
  // and set to 'action' when the server is awaiting an action.

  // actionlist is the list of available actions, when awaiting == 'action'.
  awaiting = null
  actionlist = null

  events = new WebSocket("ws://" + location.host + "/api/game");
  events.onmessage = incomingEvent;

  chat = new WebSocket("ws://" + location.host + "/api/chat");
  chat.onmessage = chatEvent;


  allnodenames = [
    "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "a9", "a10", "a11", "a12", "a13",
    "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10", "b11", "b12", "b13",
    "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10", "c11", "c12", "c13"
    ];

  var allbluestones = document.getElementsByClassName("bluestone");
  for (var i = 0; i < allbluestones.length; i++) {
    allbluestones[i].addEventListener('click', function () {nodeClick(this);}, false);
  };

  document.getElementById("flourish1").addEventListener(
    'click', function() {spellClick(this);}, false);

  document.getElementById("flourish2").addEventListener(
    'click', function() {spellClick(this);}, false);

  document.getElementById("flourish3").addEventListener(
    'click', function() {spellClick(this);}, false);

  document.getElementById("grow1").addEventListener(
    'click', function() {spellClick(this);}, false);

  document.getElementById("grow2").addEventListener(
    'click', function() {spellClick(this);}, false);

  document.getElementById("grow3").addEventListener(
    'click', function() {spellClick(this);}, false);



  document.getElementById("dashbutton").addEventListener(
    'click', function() {dashClick(this);}, false);

  document.getElementById("passbutton").addEventListener(
    'click', function() {passClick(this);}, false);

}


function dashClick(button) {
  if ((awaiting == 'action') && actionlist.includes("dash")) {
    var payload = {"message": "dash"};
    events.send(JSON.stringify(payload));
  };

}


function passClick(button) {
  if ((awaiting == 'action') && actionlist.includes("pass")) {
    var payload = {"message": "pass"};
    events.send(JSON.stringify(payload));
    document.getElementById("dashbutton").style.visibility = "hidden";
    document.getElementById("passbutton").style.visibility = "hidden";

  };
}




function spellClick(spell) {
  const capitalized = spell.id.charAt(0).toUpperCase() + spell.id.slice(1);
  if ((awaiting == 'action') && actionlist.includes(capitalized)) {
    var payload = {'message': capitalized};
    events.send(JSON.stringify(payload));
    awaiting = null;

  };


}

function nodeClick(node) {
  if (awaiting == 'node') {
    var payload = {'message': node.id.slice(4), };
    events.send(JSON.stringify(payload));
    awaiting = null;
  } else if (awaiting == 'action') {

      if (actionlist.includes('Sprout1') && node.id == 'bluea7') {
      var payload = {'message': 'Sprout1', };
      events.send(JSON.stringify(payload));
      awaiting = null;

    } else if (actionlist.includes('Sprout2') && node.id == 'blueb7') {
      var payload = {'message': 'Sprout2', };
      events.send(JSON.stringify(payload));
      awaiting = null;

    } else if (actionlist.includes('Sprout3') && node.id == 'bluec7') {
      var payload = {'message': 'Sprout3', };
      events.send(JSON.stringify(payload));
      awaiting = null;

    } else if (actionlist.includes('move')) {
      var payload = {'message': node.id.slice(4), };
      events.send(JSON.stringify(payload));
      awaiting = null;


    };

  };
  
}



function incomingEvent(event) {
  var payload = JSON.parse(event.data);
  var box = document.getElementById('actionBox');
  if (payload.type == "message") {
    box.innerHTML += "<br/>" + payload.message;
  } else if (payload.type == "boardstate") {
    updateBoard(payload);
  };
  if (payload.awaiting) {
    awaiting = payload.awaiting;
  };
  if (payload.actionlist) {
    actionlist = payload.actionlist;


    if (actionlist.includes('dash')) {
      document.getElementById("dashbutton").style.visibility = "visible";
    } else {document.getElementById("dashbutton").style.visibility = "hidden";
    };

    if (actionlist.includes('pass')) {
      document.getElementById("passbutton").style.visibility = "visible";
    } else {
      document.getElementById("passbutton").style.visibility = "hidden";
    };

  };
}



function updateBoard(boardstate) {
  for (var name of allnodenames) {
    if (boardstate[name] == "red") {
      document.getElementById("blue" + name).style.opacity = 0;
      document.getElementById("red" + name).style.opacity = 1;
    } else if (boardstate[name] == "blue") {
      document.getElementById("red" + name).style.opacity = 0;
      document.getElementById("blue" + name).style.opacity = 1;
    } else {
      document.getElementById("red" + name).style.opacity = 0;
      document.getElementById("blue" + name).style.opacity = 0;
    };
    
 
  };


  }





function actionInputKeypress(e) {
  e = e || window.event;
  if (e.keyCode == 13) {
    var message = document.getElementById('actionInput').value;
    var payload = {"message": message};
    events.send(JSON.stringify(payload));
    document.getElementById('actionInput').value = '';
  };
}

function chatEvent(event) {
  var payload = JSON.parse(event.data);
  document.getElementById('chatBox').innerHTML += '<br /><b>Player ' + payload.player + '</b>: ' + payload.message;
  return false;
}


function chatInputKeypress(e) {
  e = e || window.event;
  if (e.keyCode == 13) {
    var message = document.getElementById('chatInput').value;
    var payload = {"message": message};
    chat.send(JSON.stringify(payload));
    document.getElementById('chatInput').value = '';
  };
}







