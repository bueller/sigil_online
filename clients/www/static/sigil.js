

function main() {
  // awaiting is a global variable set to null when not awaiting anything,
  // set to 'node' when the server is awaiting a node name,
  // and set to 'action' when the server is awaiting an action.

  // actionlist is the list of available actions, when awaiting == 'action'.

  awaiting = null;
  actionlist = null;
  joinedgame = false;


  // SpellDict will be a dictionary with keys "major2", "charm3", etc.,
  // and values "Flourish2", "Sprout3", etc.
  SpellDict = null;


  // ReverseSpellDict will be a dictionary with keys "Flourish2", "Sprout3", etc.,
  // and values "major2", "charm3", etc.
  ReverseSpellDict = null;


  auxlockdict = {
    "major1": "a1",
    "major2": "b1",
    "major3": "c1",
    "minor1": "a2",
    "minor2": "b2",
    "minor3": "c2",
  };

  // lockdict will be a dictionary with keys "Flourish2", "Sprout3", etc.,
  // and values "a1", "c2", etc.  It is initialized at the same time as SpellDict,
  // once the spell setup JSON is received.
  lockdict = {};

  for (spellname in ReverseSpellDict) {
    lockdict[spellname] = auxlockdict[ReverseSpellDict[spellname]];
  };



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

  document.getElementById("major1").addEventListener(
    'click', function() {spellClick(this.id);}, false);

  document.getElementById("major2").addEventListener(
    'click', function() {spellClick(this.id);}, false);

  document.getElementById("major3").addEventListener(
    'click', function() {spellClick(this.id);}, false);

  document.getElementById("minor1").addEventListener(
    'click', function() {spellClick(this.id);}, false);

  document.getElementById("minor2").addEventListener(
    'click', function() {spellClick(this.id);}, false);

  document.getElementById("minor3").addEventListener(
    'click', function() {spellClick(this.id);}, false);



  document.getElementById("dashbutton").addEventListener(
    'click', function() {dashClick(this);}, false);

  document.getElementById("passbutton").addEventListener(
    'click', function() {passClick(this);}, false);

  document.getElementById("resetbutton").addEventListener(
    'click', function() {resetClick(this);}, false);

  document.getElementById("startbutton").addEventListener(
    'click', function() {startClick(this);}, false);

  document.addEventListener("keydown", keyDownFunction, false);


setInterval(ping, 3000);


}


function spellClick(spellposition) {
  // Takes in a spell position, e.g., "major2", "minor3"
  var spellname = SpellDict[spellposition];
  if ((awaiting == 'action') && actionlist.includes(spellname)) {
    var payload = {'message': spellname};
    events.send(JSON.stringify(payload));
    awaiting = null;

  };

}


function setupSpells(spellnamedict) {
  // spellnamedict is a JSON dictionary with keys "major2", "charm3", etc.,
  // and values "Flourish2", "Sprout3", etc.
  document.getElementById("major1").src = "images/" + spellnamedict.major1.slice(0, -1) + ".png";
  document.getElementById("major2").src = "images/" + spellnamedict.major2.slice(0, -1) + ".png";
  document.getElementById("major3").src = "images/" + spellnamedict.major3.slice(0, -1) + ".png";
  document.getElementById("minor1").src = "images/" + spellnamedict.minor1.slice(0, -1) + ".png";
  document.getElementById("minor2").src = "images/" + spellnamedict.minor2.slice(0, -1) + ".png";
  document.getElementById("minor3").src = "images/" + spellnamedict.minor3.slice(0, -1) + ".png";
  document.getElementById("charm1").src = "images/" + spellnamedict.charm1.slice(0, -1) + ".png";
  document.getElementById("charm2").src = "images/" + spellnamedict.charm2.slice(0, -1) + ".png";
  document.getElementById("charm3").src = "images/" + spellnamedict.charm3.slice(0, -1) + ".png";
}


function fadeIn() {
  document.getElementById("startbutton").style.display = "none";

  document.getElementById("board").style.opacity = 1;
  document.getElementById("major3").style.opacity = 1;
  document.getElementById("minor2").style.opacity = 1;
  document.getElementById("charm2").style.opacity = 1;
  document.getElementById("major2").style.opacity = 1;
  document.getElementById("minor1").style.opacity = 1;
  document.getElementById("charm1").style.opacity = 1;
  document.getElementById("major1").style.opacity = 1;
  document.getElementById("minor3").style.opacity = 1;
  document.getElementById("charm3").style.opacity = 1;

  document.getElementById("chatInput").style.visibility = "visible";
  document.getElementById("chatBox").style.opacity = 1;
  document.getElementById("chatInput").style.opacity = 1;

  setTimeout(scorekeeperFadeIn, 3500);
}

function scorekeeperFadeIn (){
  document.getElementById("scorekeeper").style.opacity = 1;
}



function ping() {
  var payload = {"message": "ping"};
  events.send(JSON.stringify(payload));
  chat.send(JSON.stringify(payload));
}

function keyDownFunction(e) {
  if (e.target == document.getElementById("chatInput")) {;} else {
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


function resetClick(button) {
  awaiting = null;
  actionlist = null;
  var payload = {'message': 'reset'};
  events.send(JSON.stringify(payload));
}

function startClick(button) {
  joinedgame = true;
  var payload = {'message': 'joinedgame'};
  events.send(JSON.stringify(payload));
  fadeIn();
}





function nodeClick(node) {
  if (joinedgame){
  if (awaiting == 'node') {
    var payload = {'message': node.id.slice(4), };
    events.send(JSON.stringify(payload));
    awaiting = null;
  } else if (awaiting == 'action') {

      if (actionlist.includes(SpellDict['charm1']) && node.id == 'bluea7') {
      var payload = {'message': SpellDict['charm1'], };
      events.send(JSON.stringify(payload));
      awaiting = null;

    } else if (actionlist.includes(SpellDict['charm2']) && node.id == 'blueb7') {
      var payload = {'message': SpellDict['charm2'], };
      events.send(JSON.stringify(payload));
      awaiting = null;

    } else if (actionlist.includes(SpellDict['charm3']) && node.id == 'bluec7') {
      var payload = {'message': SpellDict['charm3'], };
      events.send(JSON.stringify(payload));
      awaiting = null;

    } else if (actionlist.includes('move')) {
      var payload = {'message': node.id.slice(4), };
      events.send(JSON.stringify(payload));
      awaiting = null;


    };

  };
  };
}



function incomingEvent(event) {
  var payload = JSON.parse(event.data);
  var box = document.getElementById('actionBox');

  if (payload.type == "pong") {;} else if (payload.type == "spellsetup") {

    SpellDict = payload;
    delete SpellDict['type'];

    ReverseSpellDict = {};
    for (position in SpellDict) {ReverseSpellDict[SpellDict[position]] = position;};

    for (spellname in ReverseSpellDict) {
    lockdict[spellname] = auxlockdict[ReverseSpellDict[spellname]];
    };


    console.log(SpellDict);
    console.log(ReverseSpellDict);






    setupSpells(payload);

  } else if (payload.type == "message") {
    box.innerHTML += "<br/>" + payload.message;

    box.scrollTop = box.scrollHeight;
    
  } else if (payload.type == "whoseturndisplay") {
    var turnbox = document.getElementById("whoseturndisplay");
    if (payload.color == "red") {
      turnbox.style.color = "Crimson";
    }
    else if (payload.color == "blue") {
      turnbox.style.color = "Blue";
    }
    turnbox.innerHTML = payload.message;

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



  } else if (payload.type == "chooserefills") {

    for (nodename of allnodenames) {
      if (payload[nodename]) {
        document.getElementById(payload.playercolor + nodename).style.opacity = .5;
      };
    };

  } else if (payload.type == "donerefilling") {
    for (nodename of allnodenames) {
      if (document.getElementById(payload.playercolor + nodename).style.opacity == .5) {
        document.getElementById(payload.playercolor + nodename).style.opacity = 0;

      };
    };
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




    var redlockedspellname = boardstate["redlock"];
    var bluelockedspellname = boardstate["bluelock"];
    // These are the locked spell names, e.g., "Flourish2", "Grow3"

    for (lockIdentifierChars of ['a1', 'b1', 'c1', 'a2', 'b2', 'c2']){
      if ((document.getElementById("redlockcircle" + lockIdentifierChars).className == "redlockcircleend") &&
        lockdict[redlockedspellname] != lockIdentifierChars) {
        deactivateLock(lockIdentifierChars, "red");
      };

      if ((document.getElementById("redlockcircle" + lockIdentifierChars + "alt").className == "redlockcircleend") &&
        lockdict[redlockedspellname] != lockIdentifierChars) {
        deactivateLock(lockIdentifierChars + "alt", "red");
      };

      if ((document.getElementById("bluelockcircle" + lockIdentifierChars).className == "bluelockcircleend") &&
        lockdict[bluelockedspellname] != lockIdentifierChars) {
        deactivateLock(lockIdentifierChars, "blue");
      };

      if ((document.getElementById("bluelockcircle" + lockIdentifierChars + "alt").className == "bluelockcircleend") &&
        lockdict[bluelockedspellname] != lockIdentifierChars) {
        deactivateLock(lockIdentifierChars + "alt", "blue");
      };
    };

    if (redlockedspellname) {
      if ((document.getElementById("redlockcircle" + lockdict[redlockedspellname]).className == "redlockcirclestart") &&
        (document.getElementById("redlockcircle" + lockdict[redlockedspellname] + "alt").className == "redlockcirclestart")) {
        if (document.getElementById("bluelockcircle" + lockdict[redlockedspellname]).className == "bluelockcirclestart"){
          activateLock(lockdict[redlockedspellname], "red");
        } else {activateLock(lockdict[redlockedspellname] + "alt", "red");
        };

      };

    };

    if (bluelockedspellname) {
      if ((document.getElementById("bluelockcircle" + lockdict[bluelockedspellname]).className == "bluelockcirclestart") &&
        (document.getElementById("bluelockcircle" + lockdict[bluelockedspellname] + "alt").className == "bluelockcirclestart")) {
        if (document.getElementById("redlockcircle" + lockdict[bluelockedspellname]).className == "redlockcirclestart"){
          activateLock(lockdict[bluelockedspellname], "blue");
        } else {activateLock(lockdict[bluelockedspellname] + "alt", "blue");
        };

      };

    };



    var score = boardstate["score"];
    if (score) {
      document.getElementById("scorekeeper").className = "score" + score;
    };

    var countdown = boardstate["countdown"];
    document.getElementById("countdown").innerHTML = countdown;

  }


function activateLock(lockIdentifierChars, color) {
  document.getElementById(color + "lock" + lockIdentifierChars).className = color + "lock" + lockIdentifierChars + "end";
  document.getElementById(color + "lockcircle" + lockIdentifierChars).className = color + "lockcircleend";
  document.getElementById(color + "leftbar" + lockIdentifierChars).className = color + "leftbarend";
  document.getElementById(color + "rightbar" + lockIdentifierChars).className = color + "rightbarend";
  document.getElementById(color + "topbar" + lockIdentifierChars).className = color + "topbarend";
  document.getElementById(color + "bottombar" + lockIdentifierChars).className = color + "bottombarend";
}

function deactivateLock(lockIdentifierChars, color) {
  document.getElementById(color + "lock" + lockIdentifierChars).className = color + "lock" + lockIdentifierChars +"start";
  document.getElementById(color + "lockcircle" + lockIdentifierChars).className = color + "lockcirclestart";
  document.getElementById(color + "leftbar" + lockIdentifierChars).className = color + "leftbarstart";
  document.getElementById(color + "rightbar" + lockIdentifierChars).className = color + "rightbarstart";
  document.getElementById(color + "topbar" + lockIdentifierChars).className = color + "topbarstart";
  document.getElementById(color + "bottombar" + lockIdentifierChars).className = color + "bottombarstart";
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
  var box = document.getElementById('chatBox');
  if (payload.type == "pong") {;} else if (payload.type == "chatmessage") {
  box.innerHTML += '<br /><b>' + payload.player + '</b> ' + payload.message;
  box.scrollTop = box.scrollHeight;
  };
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







