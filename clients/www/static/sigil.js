

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

  document.addEventListener("keydown", keyDownFunction, false);


  lockdict = {
    "Flourish1red": "redlock_a_big_solo",
    "Flourish2red": "redlock_b_big_solo",
    "Flourish3red": "redlock_c_big_solo",
    "Grow1red": "redlock_a_med_solo",
    "Grow2red": "redlock_b_med_solo",
    "Grow3red": "redlock_c_med_solo",

    "Flourish1blue": "bluelock_a_big_solo",
    "Flourish2blue": "bluelock_b_big_solo",
    "Flourish3blue": "bluelock_c_big_solo",
    "Grow1blue": "bluelock_a_med_solo",
    "Grow2blue": "bluelock_b_med_solo",
    "Grow3blue": "bluelock_c_med_solo",

    "Flourish1blue2": "bluelock_a_big_duo",
    "Flourish2blue2": "bluelock_b_big_duo",
    "Flourish3blue2": "bluelock_c_big_duo",
    "Grow1blue2": "bluelock_a_med_duo",
    "Grow2blue2": "bluelock_b_med_duo",
    "Grow3blue2": "bluelock_c_med_duo",
  };

}

function keyDownFunction(e) {
  var keyCode = e.keyCode;
  if (keyCode == 32) {
    e.preventDefault();
    if (document.getElementById("passbutton").style.visibility == "visible") {
      document.getElementById("passbutton").click();
    };
  } else if (keyCode == 68) {
    if (document.getElementById("dashbutton").style.visibility == "visible") {
      document.getElementById("dashbutton").click();
    };
  } else if (keyCode == 82) {
    if (document.getElementById("resetbutton").style.visibility == "visible") {
      document.getElementById("resetbutton").click();

    };
  };
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
    document.getElementById("resetbutton").style.visibility = "hidden";

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

    box.scrollTop = box.scrollHeight;
    
  } else if (payload.type == "boardstate") {
    updateBoard(payload);
  } else if (payload.type == "pushingoptions") {
    for (nodename of allnodenames) {
      if (payload[nodename]) {
        document.getElementById(payload[nodename] + nodename).style.opacity = .5;
      };
    };
  } else if (payload.type == "firstturnpass") {
    awaiting = 'action';
    actionlist = [ "pass" ];
    document.getElementById("passbutton").style.visibility = "visible";
    document.getElementById("resetbutton").style.visibility = "visible";


  };


  if (payload.awaiting) {
    awaiting = payload.awaiting;
  };
  if (payload.actionlist) {
    actionlist = payload.actionlist;
    document.getElementById("resetbutton").style.visibility = "visible";


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

  console.log("Board Update");
  
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


    for (var lock in lockdict) {
      document.getElementById(lockdict[lock]).style.opacity = 0;
    };

    var redlockedspellname = boardstate["redlock"];
    var bluelockedspellname = boardstate["bluelock"];

    if (redlockedspellname){
      document.getElementById(lockdict[redlockedspellname + "red"]).style.opacity = 1;
    };

    if (bluelockedspellname) {
      if (redlockedspellname == bluelockedspellname) {
        document.getElementById(lockdict[bluelockedspellname + "blue2"]).style.opacity = 1;
      } else {
        document.getElementById(lockdict[bluelockedspellname + "blue"]).style.opacity = 1;
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







