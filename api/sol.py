### Sigil Online




import json
import time

import gevent
from flask import Flask
from flask_sockets import Sockets
from random import randint

import sol_spells

# The only core game feature
# not yet implemented is detecting that the game
# is going in a loop (after 5 repeats of the board state)
# and making blue win in this case (after giving red fair warning).
# But I'll save that for another time.




class Node():
    def __init__(self, name):
        self.name = name

        ### neighbors is a list of node objects which are adjacent
        self.neighbors = []

        ### stone is None when empty, 'red' or 'blue' when filled
        self.stone = None


class Spell():
    def __init__(self, board, position, name):
        self.board = board

        ### position is a list of the node objects
        ### which constitute this spell.
        self.position = position

        self.name = name

        ### True iff it's a charm
        self.ischarm = False

        ### True iff it's static
        self.static = False

        ### The 'charged' attribute will equal 'red' or 'blue'
        ### if one of them has the spell fully charged, and None otherwise
        self.charged = None

        ### Overwrite these in the actual spell classes.
        ### Note that two_sigil_refill is just the EXTRA refill from
        ### second sigil. (which you will ADD to the one_sigil_refill)
        self.one_sigil_refill = 0
        self.two_sigil_refill = 0

    def cast(self, player):
        ### sacrifice all stones in it, and refill appropriate
        ### number based on sigils
        pname = player.color[0].upper() + player.color[1:]
        jmessage(player.ws, pname + " casts " + self.name)
        jmessage(player.opp.ws, pname + " casts " + self.name)
        if self.ischarm:
            for node in self.position:
                node.stone = None

        elif player.sigils == 3:
            pass

        else:
            for node in self.position:
                node.stone = None

            if player.sigils == 0:
                refills = 0

            elif player.sigils == 1:
                refills = self.one_sigil_refill

            elif player.sigils == 2:
                refills = self.one_sigil_refill + self.two_sigil_refill

            if refills > 1:
                jmessage(player.ws, "You get to keep {} stones in ".format(refills)
                               + self.name + ".")
            elif refills == 1:
                jmessage(player.ws, "You get to keep 1 stone in " + self.name + ".")

            while refills > 0:
                jmessage(player.ws, "Select a stone to keep: ", "node")

                egress = { "type": "chooserefills", "playercolor": player.color }

                for node in self.position:
                    if node.stone == None:
                        egress[node.name] = "True"

                player.ws.send(json.dumps(egress))

                while True:
                    ingress = player.ws.receive()
                    if json.loads(ingress)['message'] == 'ping':
                        pong(player.ws)
                        pong(player.opp.ws)
                        continue
                    else:
                        break
                
                if json.loads(ingress)['message'] == 'reset':
                    raise resetException()

                keep = json.loads(ingress)['message']
                
                if self.board.nodes[keep] not in self.position:
                    jmessage(player.ws, "That's not a node in your spell!")

                elif self.board.nodes[keep].stone != None:
                    jmessage(player.ws, "You already kept that stone!")
                    continue
                else:
                    refills -= 1
                    self.board.nodes[keep].stone = player.color
                    self.board.update()

            egress = { "type": "donerefilling" , "playercolor": player.color}
            player.ws.send(json.dumps(egress))
            
        self.board.update()
        self.resolve(player)

        ### Update the score on board
        self.board.update(True)

        if not self.ischarm:
            player.lock = self
            self.board.countdown -= 1

    def resolve(self, player):
        ### The actual effect!!!
        ### Overwrite this in the specific spell classes.
        pass

    def update_charge(self):
        ### Sets the 'charged' attribute to correctly reflect
        ### the current board state.  Must be called every time
        ### the board state changes.

        firststone = self.position[0].stone
        if len(self.position) == 1:
            self.charged = firststone
            return None
        else:
            for node in self.position[1:]:
                if node.stone != firststone:
                    self.charged = None
                    return None
            self.charged = firststone



########################################################
########################################################
########################################################
########################################################
########################################################

#####  ACTUAL SPELLS HERE


class Sprout(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.ischarm = True

        self.text = "<b>Sprout</b><br />Make 1 soft move."


    def resolve(self, player):
        player.softmove()


class Stomp(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.ischarm = True

        self.text = "<b>Stomp</b><br />Make 1 hard move.<br />Counts as your dash."


    def resolve(self, player):
        ### The behavior about "counting as your dash" is implemented
        ### in the player.taketurn method.
        player.hardmove()


class Shadow(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.ischarm = True

        self.text = "<b>Shadow</b><br />Make 1 move into<br />a locked spell or Sigil."


    def resolve(self, player):
        player.move(shadowing=True)



class Blink(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.ischarm = True

        self.text = "<b>Blink</b><br />Put a stone into any empty node,<br />then sacrifice a stone."


    def resolve(self, player):
        
        while True:
            jmessage(player.ws, "Where would you like to Blink?", "node")
            while True:
                ingress = player.ws.receive()
                if json.loads(ingress)['message'] == 'ping':
                    pong(player.ws)
                    pong(player.opp.ws)
                    continue
                else:
                    break
                
            if json.loads(ingress)['message'] == 'reset':
                raise resetException()

            actualmessage = json.loads(ingress)['message']

            if actualmessage in board.nodes:
                node = board.nodes[actualmessage]
                if node.stone != None:
                    jmessage(player.ws, "Invalid option")
                    continue

                else:
                    node.stone = player.color
                    board.update()
                    break

            else:
                continue

        while True:
            jmessage(player.ws, "Select a stone to sacrifice.", "node")
            while True:
                ingress = player.ws.receive()
                if json.loads(ingress)['message'] == 'ping':
                    pong(player.ws)
                    pong(player.opp.ws)
                    continue
                else:
                    break
                
            if json.loads(ingress)['message'] == 'reset':
                raise resetException()

            actualmessage = json.loads(ingress)['message']

            if actualmessage in board.nodes:
                node = board.nodes[actualmessage]
                if node.stone != player.color:
                    continue

                else:
                    node.stone = None
                    break

            else:
                continue




class Gust(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.ischarm = True

        self.text = "<b>Gust</b><br />Relocate up to 2 enemy stones<br />which are touching you<br />into any empty nodes."


    def resolve(self, player):

        egress = {"type": "selecting"}
        player.ws.send(json.dumps(egress))

        gustingstonecount = 0

        while True:
            jmessage(player.ws, "Select an enemy stone to Gust, or press Done if you are done selecting.", "node")
        
            while True:
                ingress = player.ws.receive()
                if json.loads(ingress)['message'] == 'ping':
                    pong(player.ws)
                    pong(player.opp.ws)
                    continue
                else:
                    break
                
            if json.loads(ingress)['message'] == 'reset':
                raise resetException()

            actualmessage = json.loads(ingress)['message']

            if actualmessage == 'doneselecting':
                break

            elif actualmessage in board.nodes:
                node = board.nodes[actualmessage]
                if node.stone != player.enemy:
                    jmessage(player.ws, "Invalid selection")
                    continue
                adjacent = False
                for neighbor in node.neighbors:
                    if neighbor.stone == player.color:
                        adjacent = True
                if not adjacent:
                    jmessage(player.ws, "Invalid selection")
                    continue

                node.stone = None
                board.update()
                gustingstonecount += 1
                if gustingstonecount == 2:
                    break
            else:
                continue

        egress = {"type": "doneselecting"}
        player.ws.send(json.dumps(egress))

        while gustingstonecount > 0:
            jmessage(player.ws, "Where would you like to Gust the enemy stone?", "node")

            while True:
                ingress = player.ws.receive()
                if json.loads(ingress)['message'] == 'ping':
                    pong(player.ws)
                    pong(player.opp.ws)
                    continue
                else:
                    break
                
            if json.loads(ingress)['message'] == 'reset':
                raise resetException()

            actualmessage = json.loads(ingress)['message']

            if actualmessage in board.nodes:
                node = board.nodes[actualmessage]
                if node.stone != None:
                    jmessage(player.ws, "Invalid selection")
                    continue

                gustingstonecount -= 1
                node.stone = player.enemy
                board.update()

            else:
                continue




class Grow(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.one_sigil_refill = 0
        self.two_sigil_refill = 1

        self.text = "<b>Grow</b><br /><img src='images/moonrefill.png' class='moonrefill'><br />Make 3 soft moves."

    def resolve(self, player):
        for i in range(3):
            player.softmove()


class Thunder(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.one_sigil_refill = 0
        self.two_sigil_refill = 1

        self.text = "<b>Thunder</b><br /><img src='images/moonrefill.png' class='moonrefill'><br />Destroy up to 3 enemy stones<br />in any one spell."

    def resolve(self, player):
        ### IMPLEMENT THIS
        
        while True:
            jmessage(player.ws, "Select a spell.", "spell")
            while True:
                ingress = player.ws.receive()
                if json.loads(ingress)['message'] == 'ping':
                    pong(player.ws)
                    pong(player.opp.ws)
                    continue
                else:
                    break
                
            if json.loads(ingress)['message'] == 'reset':
                raise resetException()

            actualmessage = json.loads(ingress)['message']

            if actualmessage in board.spelldict:
                chosenspell = board.spelldict[actualmessage]
                break

            else:
                continue

        egress = {"type": "selecting"}
        player.ws.send(json.dumps(egress))

        
        destroyedcount = 0
        while destroyedcount <3:
            jmessage(player.ws, "Select an enemy stone in " + chosenspell.name[:-1] + " to destroy, or press Done if you are done selecting.", "node")

            while True:
                ingress = player.ws.receive()
                if json.loads(ingress)['message'] == 'ping':
                    pong(player.ws)
                    pong(player.opp.ws)
                    continue
                else:
                    break
                
            if json.loads(ingress)['message'] == 'reset':
                raise resetException()

            actualmessage = json.loads(ingress)['message']

            if actualmessage == 'doneselecting':
                break

            elif actualmessage in board.nodes:
                node = board.nodes[actualmessage]
                if node.stone != player.enemy:
                    jmessage(player.ws, "Invalid selection")
                    continue
                
                if not (node in chosenspell.position):
                    jmessage(player.ws, "Invalid selection")
                    continue

                node.stone = None
                board.update()
                destroyedcount += 1
                
            else:
                continue

        egress = {"type": "doneselecting"}
        player.ws.send(json.dumps(egress))



        


class Levity(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.one_sigil_refill = 0
        self.two_sigil_refill = 0

        self.static = True

        self.text = "<b>Levity</b><br /><span style='color:BlueViolet;'>Static</span><br />You may put a stone into any empty node<br />as your standard move each turn."




class Flourish(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.one_sigil_refill = 1
        self.two_sigil_refill = 1

        self.text = "<b>Flourish</b><br /><img src='images/sunrefill.png' class='sunrefill'><img src='images/moonrefill.png' class='moonrefill'><br />Make 4 soft moves."

    def resolve(self, player):
        for i in range(4):
            player.softmove()

class Fury(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.one_sigil_refill = 0
        self.two_sigil_refill = 0

        self.text = "<b>Fury</b><br /><br />Make 3 hard moves."

    def resolve(self, player):
        for i in range(3):
            player.hardmove()

class Onslaught(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.one_sigil_refill = 0
        self.two_sigil_refill = 2

        self.text = "<b>Onslaught</b><br /><img src='images/moonrefill.png' class='moonrefill'><img src='images/moonrefill.png' class='moonrefill'><br />Make 4 hard moves."

    def resolve(self, player):
        for i in range(4):
            player.hardmove()


class Fire(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.one_sigil_refill = 0
        self.two_sigil_refill = 1

        self.text = "<b>Fire</b><br /><img src='images/moonrefill.png' class='moonrefill'><br />Destroy all enemy stones<br />which are touching you."

    def resolve(self, player):
        for name in board.nodes:
            node = board.nodes[name]
            if node.stone == player.enemy:
                for neighbor in node.neighbors:
                    if neighbor.stone == player.color:
                        node.stone = None


class Ice(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.one_sigil_refill = 0
        self.two_sigil_refill = 1

        self.text = "<b>Ice</b><br /><img src='images/moonrefill.png' class='moonrefill'><br />Destroy up to 1 enemy stone<br />in each spell and charm."

    def resolve(self, player):

        egress = {"type": "selecting"}
        player.ws.send(json.dumps(egress))

        iceablespells = []
        ### We will use the notation of board.positions to refer to spells.
        ### That is, 1,2,3 are the majors, 4,5,6 are the minors, 7,8,9 charms.

        for i in range(1,10):
            innernodelist = board.positions[i]
            for node in innernodelist:
                if node.stone == player.enemy:
                    iceablespells.append(i)
                    break

        while len(iceablespells) > 0:
            jmessage(player.ws, "Select an enemy stone to destroy, or press Done if you are done selecting.", "node")

            while True:
                ingress = player.ws.receive()
                if json.loads(ingress)['message'] == 'ping':
                    pong(player.ws)
                    pong(player.opp.ws)
                    continue
                else:
                    break
                
            if json.loads(ingress)['message'] == 'reset':
                raise resetException()

            actualmessage = json.loads(ingress)['message']

            if actualmessage == 'doneselecting':
                break

            elif actualmessage in board.nodes:
                node = board.nodes[actualmessage]

                if node.stone != player.enemy:
                    jmessage(player.ws, "Invalid selection")
                    continue

                validstone = False

                for spellnum in iceablespells:
                    if node in board.positions[spellnum]:
                        node.stone = None
                        iceablespells.remove(spellnum)
                        board.update()
                        continue

                jmessage(player.ws, "Invalid selection")
                continue
                
            else:
                continue

        egress = {"type": "doneselecting"}
        player.ws.send(json.dumps(egress))




class Syzygy(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.one_sigil_refill = 1
        self.two_sigil_refill = 1

        self.text = "<b>Syzygy</b><br /><img src='images/sunrefill.png' class='sunrefill'><img src='images/moonrefill.png' class='moonrefill'><br />Fill the minor spell and charm<br />across the board from Syzygy<br />with your stones. Relocate<br />all enemy stones that were there<br />into any empty nodes."

    def resolve(self, player):
        myposition = self.name[-1:]
        if myposition == '1':
            oppositenodes = board.positions[5] + board.positions[8]
        elif myposition == '2':
            oppositenodes = board.positions[6] + board.positions[9]
        elif myposition == '3':
            oppositenodes = board.positions[4] + board.positions[7]

        enemycount = 0
        for node in oppositenodes:
            if node.stone == player.enemy:
                enemycount += 1
        for node in oppositenodes:
            node.stone = player.color
            board.update()

        jmessage(player.ws, "There are " + str(enemycount) + " enemy stones to relocate.")
        while enemycount > 0:
            jmessage(player.ws, "Where would you like to relocate it?", "node")

            while True:
                ingress = player.ws.receive()
                if json.loads(ingress)['message'] == 'ping':
                    pong(player.ws)
                    pong(player.opp.ws)
                    continue
                else:
                    break
                
            if json.loads(ingress)['message'] == 'reset':
                raise resetException()

            actualmessage = json.loads(ingress)['message']

            if actualmessage in board.nodes:
                node = board.nodes[actualmessage]
                if node.stone != None:
                    jmessage(player.ws, "Invalid selection")
                    continue

                enemycount -= 1
                node.stone = player.enemy
                board.update()

            else:
                continue




class Bewitch(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.one_sigil_refill = 1
        self.two_sigil_refill = 1

        self.text = "<b>Bewitch</b><br /><img src='images/sunrefill.png' class='sunrefill'><img src='images/moonrefill.png' class='moonrefill'><br />Choose any 2 enemy stones<br />which are touching each other.<br />Convert them to your color."

    def resolve(self, player):

        egress = {"type": "selectingNoButton"}
        player.ws.send(json.dumps(egress))

        while True:
            jmessage(player.ws, "Select an enemy stone to convert.", "node")

            while True:
                ingress = player.ws.receive()
                if json.loads(ingress)['message'] == 'ping':
                    pong(player.ws)
                    pong(player.opp.ws)
                    continue
                else:
                    break
                                
            if json.loads(ingress)['message'] == 'reset':
                raise resetException()

            actualmessage = json.loads(ingress)['message']

            if actualmessage in board.nodes:
                node = board.nodes[actualmessage]

                if node.stone != player.enemy:
                    jmessage(player.ws, "Invalid selection")
                    continue

                validstone = False

                for neighbor in node.neighbors:
                    if neighbor.stone == player.enemy:
                        validstone = True

                if validstone:
                    node.stone = player.color
                    board.update()
                    break

                else:
                    jmessage(player.ws, "Invalid selection")
                    continue

            else:
                continue

        while True:
            jmessage(player.ws, "Select an adjacent enemy stone to convert.", "node")
            while True:
                ingress = player.ws.receive()
                if json.loads(ingress)['message'] == 'ping':
                    pong(player.ws)
                    pong(player.opp.ws)
                    continue
                else:
                    break
                        
            if json.loads(ingress)['message'] == 'reset':
                raise resetException()

            actualmessage = json.loads(ingress)['message']

            if actualmessage in board.nodes:
                node2 = board.nodes[actualmessage]

                if node2.stone != player.enemy:
                    jmessage(player.ws, "Invalid selection")
                    continue

                validstone = False
                for neighbor in node2.neighbors:
                    if neighbor == node:
                        validstone = True

                if not validstone:
                    jmessage(player.ws, "Invalid selection")
                    continue

                else:
                    node2.stone = player.color
                    board.update()
                    break

            else:
                continue



class Nirvana(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.one_sigil_refill = 0
        self.two_sigil_refill = 0

        self.static = True

        self.text = "<b>Nirvana</b><br /><span style='color:BlueViolet;'>Static</span><br />Your dash each turn<br />only requires 1 sacrifice.<br />(You may sacrifice it from Nirvana.)"




class Inferno(Spell):
    def __init__(self, board, position, name):
        super().__init__(board, position, name)
        self.one_sigil_refill = 0
        self.two_sigil_refill = 0

        self.static = True

        self.text = "<b>Inferno</b><br /><span style='color:BlueViolet;'>Static</span><br />At the end of your turn, destroy all<br />enemy stones which are touching you.<br />At the start of your turn,<br />you lose the game."





    

            
        



#####  ACTUAL SPELLS FINISHED

########################################################
########################################################
########################################################
########################################################
########################################################




class Board():
    def __init__(self):
        ### nodes is a dict that takes strings (names)
        ### and returns the corresponding node objects
        self.nodes = self.make_board()

        ### positions is a dict with keys 1-9.  1,2,3 are major spells
        ### in zones a,b,c respectively.  4,5,6 are minor spells.
        ### 7,8,9 are charms.
        ### Each value is a list of nodes, the ones
        ### constituting that spell.
        self.positions = self.make_positions()

        ### spells is a list of the 9 spell objects on the board.
        ### These objects are defined by the spell class,
        ### as well as the child class corresponding to
        ### what spell it is.
        self.spells = self.make_spells()

        ### spelldict is a dictionary with keys = spell names
        ### (strings), and values which are the spell objects themselves.
        self.spelldict = self.make_spelldict()

        ### There will also be board attributes for the two players.
        ### But they will get added by the board.addplayers() method,
        ### which we call AFTER constructing the board and then
        ### constructing the players.

        ### These will be player objects after the addplayers() method
        ### is called.

        ### ONLY REFER TO THESE ATTRIBUTES
        ### after the board setup has been finished!
        self.redplayer = None
        self.blueplayer = None

        ### The spell countdown! The EOT trigger checks in
        ### player.taketurn will check if board.countdown == 0,
        ### and if so, end the game appropriately.
        self.countdown = 7



        ### A dictionary of all the relevant facts about the board state.
        ### We take a snapshot using board.take_snapshot() , and then
        ### if the user throws a 'reset' exception, the board returns to
        ### whatever state is saved in board.snapshot .
        self.snapshot = None

        ### A string that tells which player is winning and by how much.
        self.score = 'b1'


    def take_snapshot(self):

        ### ADD ALL BOARD ATTRIBUTES TO THE SNAPSHOT

        ### Sets board.snapshot to be a dictionary 
        ### which describes the current boardstate

        snapshot = {}
        snapshot["turncounter"] = turncounter
        snapshot["gameover"] = gameover
        snapshot["winner"] = winner
        snapshot["score"] = self.score
        snapshot["currentplayerhasmoved"] = currentplayerhasmoved
        for nodename in self.nodes:
            snapshot[nodename] = self.nodes[nodename].stone
        if self.redplayer.lock:
            snapshot["redlock"] = self.redplayer.lock.name
        else:
            snapshot["redlock"] = None
        
        if self.blueplayer.lock:
            snapshot["bluelock"] = self.blueplayer.lock.name
        else:
            snapshot["bluelock"] = None

        snapshot["countdown"] = self.countdown

        self.snapshot = snapshot



    def update(self, update_score = False):

        ### Updates the visual board display: which stones are where,
        ### and also which spells are locked.

        ### MAKE IT SEND INFO ON THE COUNTDOWN, TOO !!!
        ### MAKE IT SEND INFO ON THE COUNTDOWN, TOO !!!
        ### MAKE IT SEND INFO ON THE COUNTDOWN, TOO !!!

        ### Updates the status of all the spells.
        ### These statuses will be stored
        ### in the 'charged_spells' attributes of players.

        ### Also updates the players' 'sigils' and 'totalstones' attributes.

        ### board.update() MUST BE CALLED WHENEVER
        ### ANY STONE CHANGES POSITION!
        redtotalstones = 0
        bluetotalstones = 0
        for name in self.nodes:
            color = self.nodes[name].stone
            if color == 'red':
                redtotalstones += 1
            elif color == 'blue':
                bluetotalstones += 1
        self.redplayer.totalstones = redtotalstones
        self.blueplayer.totalstones = bluetotalstones

        redscore = redtotalstones
        bluescore = bluetotalstones + 1


        if update_score:
            ### score should be a string like 'r1', 'b2' , etc.
            if whoseturn == 'red':
                if currentplayerhasmoved:
                    nextmove = 'blue'
                else:
                    nextmove = 'red'

            elif whoseturn == 'blue':
                if currentplayerhasmoved:
                    nextmove = 'red'
                else:
                    nextmove = 'blue'

            if nextmove == 'red':
                if redscore >= bluescore:
                    scorenum = min(3, (redscore +1) - bluescore)
                    score = 'r' + str(scorenum)
                else:
                    scorenum = min(3, bluescore - redscore)
                    score = 'b' + str(scorenum)

            elif nextmove == 'blue':
                if bluescore >= redscore:
                    scorenum = min(3, (bluescore + 1) - redscore)
                    score = 'b' + str(scorenum)
                else:
                    scorenum = min(3, redscore - bluescore)
                    score = 'r' + str(scorenum)

            self.score = score


        redcharged = []
        bluecharged = []
        for spell in self.spells:
            spell.update_charge()
            if spell.charged == 'red':
                redcharged.append(spell)
            elif spell.charged == 'blue':
                bluecharged.append(spell)

        self.redplayer.charged_spells = redcharged
        self.blueplayer.charged_spells = bluecharged

        redsigils = 0
        bluesigils = 0

        for node in [self.nodes['a1'], self.nodes['b1'], self.nodes['c1']]:
            if node.stone == 'red':
                redsigils += 1
            elif node.stone == 'blue':
                bluesigils += 1

        self.redplayer.sigils = redsigils
        self.blueplayer.sigils = bluesigils



        ### Sends a json dictionary to the players.
        ### Tells which stones are where, and also which locks are where.

        jboard = {"type": "boardstate", }
        for name in self.nodes:
            jboard[name] = self.nodes[name].stone

        if self.redplayer.lock:
            jboard["redlock"] = self.redplayer.lock.name
        if self.blueplayer.lock:
            jboard["bluelock"] = self.blueplayer.lock.name


        if self.countdown > 1:
            countdownstring = "{} Spellcasts Remaining".format(self.countdown)
        elif self.countdown == 1:
            countdownstring = "1 Spellcast Remaining"
        elif self.countdown == 0:
            countdownstring = "Zero Spellcasts Remaining"


        jboard["countdown"] = countdownstring

        if update_score:
            jboard["score"] = self.score

        
        self.redplayer.ws.send(json.dumps(jboard))
        self.blueplayer.ws.send(json.dumps(jboard))


    def display(self, whoseturn):
        ### Displays the current board state.
        ### Gets called at the BEGINNING of each turn.
        if whoseturn == 'red':
            player = self.redplayer
        elif whoseturn == 'blue':
            player = self.blueplayer

        redlist = []
        bluelist = []
        for name in self.nodes:
            color = self.nodes[name].stone
            if color == 'red':
                redlist.append(name)
            elif color == 'blue':
                bluelist.append(name)
       

        
        redtotal = len(redlist)
        bluetotal = len(bluelist) + 1
        if whoseturn == 'red':
            if bluetotal > redtotal:
                jmessage(player.ws, "Blue is winning by " +
                               str(bluetotal - redtotal))
                jmessage(player.opp.ws, "Blue is winning by " +
                                   str(bluetotal - redtotal))
            else:
                jmessage(player.ws, "Red is winning by " +
                               str(redtotal + 1 - bluetotal))
                jmessage(player.opp.ws, "Red is winning by " +
                                   str(redtotal + 1 - bluetotal))
        elif whoseturn == 'blue':
            if redtotal > bluetotal:
                jmessage(player.ws, "Red is winning by " +
                               str(redtotal - bluetotal))
                jmessage(player.opp.ws, "Red is winning by " +
                                   str(redtotal - bluetotal))
            else:
                jmessage(player.ws, "Blue is winning by " +
                               str(bluetotal + 1 - redtotal))
                jmessage(player.opp.ws, "Blue is winning by " +
                                   str(bluetotal + 1 - redtotal))


    def end_game(self, winner):
        ### Right now this doesn't DO anything special,
        ### just prints some silly stuff.
        ### But this would be a good place to put any 'store the data'
        ### type code.
        jmessage(self.redplayer.ws, "Game over-- the winner is " + winner.upper() +
                               " !!!")
        jmessage(self.blueplayer.ws, "Game over-- the winner is " + winner.upper() +
                                " !!!")
        for i in range(3):
            jmessage(self.redplayer.ws, winner.upper() + " VICTORY")
            jmessage(self.blueplayer.ws, winner.upper() + " VICTORY")

    def make_board(self):
        nodelist = []

        for zone in ['a', 'b', 'c']:
            for number in range(1, 14):
                x = Node(zone + str(number))
                nodelist.append(x)

        for i in range(len(nodelist)):
            node = nodelist[i]
            name = node.name

            if name[1:] == '1':
                node.neighbors.append(nodelist[i + 1])
                node.neighbors.append(nodelist[i + 10])

            elif name[1:] == '2':
                node.neighbors.append(nodelist[i + 1])
                node.neighbors.append(nodelist[i + 4])
                node.neighbors.append(nodelist[i - 1])

            elif name[1:] == '3':
                node.neighbors.append(nodelist[i + 1])
                node.neighbors.append(nodelist[i + 10])
                node.neighbors.append(nodelist[i - 1])

            elif name[1:] == '4':
                node.neighbors.append(nodelist[i + 1])
                node.neighbors.append(nodelist[i + 3])
                node.neighbors.append(nodelist[i - 1])

            elif name[1:] == '5':
                node.neighbors.append(nodelist[i + 1])
                node.neighbors.append(nodelist[i + 7])
                node.neighbors.append(nodelist[i - 1])

            elif name[1:] == '6':
                node.neighbors.append(nodelist[i + 5])
                node.neighbors.append(nodelist[i - 4])
                node.neighbors.append(nodelist[i - 1])

            elif name[1:] == '7':
                node.neighbors.append(nodelist[i + 1])
                node.neighbors.append(nodelist[i - 3])

            elif name[1:] == '8':
                node.neighbors.append(nodelist[i + 1])
                node.neighbors.append(nodelist[i + 2])
                node.neighbors.append(nodelist[i - 1])

            elif name[1:] == '9':
                node.neighbors.append(nodelist[i + 1])
                node.neighbors.append(nodelist[i + 4])
                node.neighbors.append(nodelist[i - 1])

            elif name[1:] == '10':
                node.neighbors.append(nodelist[i - 2])
                node.neighbors.append(nodelist[i - 1])

            elif name[1:] == '11':
                node.neighbors.append(nodelist[i - 10])
                node.neighbors.append(nodelist[i - 5])

            elif name[1:] == '12':
                node.neighbors.append(nodelist[i - 7])

            elif name[1:] == '13':
                node.neighbors.append(nodelist[i - 10])
                node.neighbors.append(nodelist[i - 4])

        interzone_edges = []
        interzone_edges.append((nodelist[10], nodelist[35]))
        interzone_edges.append((nodelist[11], nodelist[32]))
        interzone_edges.append((nodelist[6], nodelist[24]))
        interzone_edges.append((nodelist[9], nodelist[23]))
        interzone_edges.append((nodelist[19], nodelist[37]))
        interzone_edges.append((nodelist[22], nodelist[36]))

        for x in interzone_edges:
            left = x[0]
            right = x[1]
            left.neighbors.append(right)
            right.neighbors.append(left)

        nodedict = {}
        for node in nodelist:
            nodedict[node.name] = node

        return nodedict

    def make_positions(self):
        ### Returns a dictionary d with with keys 1-9 and values = the 9
        ### positions.  1,2,3 are major spells
        ### in zones a,b,c respectively.  4,5,6 are minor spells.
        ### 7,8,9 are charms.
        ### Each of these position values is a list of nodes, the ones
        ### constituting that spell.

        n = self.nodes
        d = {}
        d[1] = [n['a2'], n['a3'], n['a4'], n['a5'], n['a6']]
        d[2] = [n['b2'], n['b3'], n['b4'], n['b5'], n['b6']]
        d[3] = [n['c2'], n['c3'], n['c4'], n['c5'], n['c6']]
        d[4] = [n['a8'], n['a9'], n['a10']]
        d[5] = [n['b8'], n['b9'], n['b10']]
        d[6] = [n['c8'], n['c9'], n['c10']]
        d[7] = [n['a7']]
        d[8] = [n['b7']]
        d[9] = [n['c7']]

        return d

    def make_spells(self):
        ### returns the list of spell objects that will be on the board

        ### spellnames is just a list of strings which are the names
        ### of the spells to be instantiated, in order of their
        ### position, 1-9.
        spellnames = sol_spells.spell_list

        ### Convert this spellnames list into a list of spell objects
        ### and return that in-order list of spell objects

        spells = []

        for x in spellnames:
            nextspell = eval(x)
            spells.append(nextspell)

        for charm in spells[6:]:
            charm.ischarm = True

        return spells

    def make_spelldict(self):
        ### Returns a dictionary which takes in names of spells
        ### and returns the spell objects.

        d = {}
        for spell in self.spells:
            d[spell.name] = spell

        return d

    def addplayers(self, redplayer, blueplayer):
        ### Call this method AFTER building the board and the players.
        ### This is my hack-y way of giving players the board as parameter,
        ### and also giving the board players as parameters.

        self.redplayer = redplayer
        self.blueplayer = blueplayer


class Player():
    ### color parameter should be 'red' or 'blue'
    def __init__(self, board, color):
        self.board = board
        self.color = color
        if self.color == 'red':
            self.enemy = 'blue'
        else:
            self.enemy = 'red'

        ### totalstones does NOT include the extra blue stone in the center.
        self.totalstones = 0

        ### charged_spells is a list of which spell objects
        ### are currently charged for this player.
        ### Gets updated whenever board.update() is called.
        self.charged_spells = []

        ### sigils is the number of sigils this player controls.
        ### Gets updated by board.update()
        self.sigils = 0



        ### player.lock is the spell object which is locked.
        ### To get its name we need player.lock.name
        self.lock = None

        ### player.opp will be the opponent player object.
        self.opp = None

        ### The player.ws attribute will be where we store
        ### the object which is the ws connection to each player.
        self.ws = None

    def taketurn(self, canmove=True, candash=True, cancharm=True, canspell=True):
        global currentplayerhasmoved
        self.board.update(True)

        actions = []
        charmlist = []
        spelllist = []
        if canmove:
            actions.append('move')
        if (candash & (self.totalstones > 2)):
            actions.append('dash')
        if cancharm:
            self.board.update()
            for spell in self.charged_spells:
                if spell.ischarm:
                    if not((spell.name[:-1] == "Stomp") and (not candash)):
                        if not spell.static:
                            actions.append(spell.name)
                            charmlist.append(spell.name)
        if not canmove:
            if canspell:
                self.board.update()
                for spell in self.charged_spells:
                    if not spell.ischarm and self.lock != spell:
                        if not spell.static:
                            actions.append(spell.name)
                            spelllist.append(spell.name)
            actions.append('pass')

        jmessage(self.ws, "\nSelect an action:")


        egress =  {"type": "message", "message": str(actions), 
        "awaiting": "action", "actionlist": actions}

        self.ws.send(json.dumps(egress))


        while True:
            ingress = self.ws.receive()
            if json.loads(ingress)['message'] == 'ping':
                pong(self.ws)
                pong(self.opp.ws)
                continue
            else:
                break


        if json.loads(ingress)['message'] == 'reset':
                    raise resetException()
        action = json.loads(ingress)['message']


        ### This clause performs the 'move' action with the node name preloaded.
        ### In this case action == the name of a node.

        if 'move' in actions:
            shortcuts = self.board.nodes.keys()
        else:
            shortcuts = []


        if action not in actions and action not in shortcuts:
            jmessage(self.ws, "Invalid action!")
            self.taketurn(canmove, candash, cancharm, canspell)
            return None

        elif action in shortcuts:
            self.move(action, standardmove=True)
            currentplayerhasmoved = True
            self.taketurn(False, candash, cancharm, canspell)
            return None

        elif action == 'move':
            self.move(standardmove=True)
            currentplayerhasmoved = True
            self.taketurn(False, candash, cancharm, canspell)
            return None

        elif action == 'dash':
            self.dash()
            self.taketurn(canmove, False, cancharm, canspell)
            return None

        elif action in charmlist:
            self.board.spelldict[action].cast(self)
            if action[:-1] == "Stomp":
                candash = False
            self.taketurn(canmove, candash, False, canspell)

        elif action in spelllist:
            self.board.spelldict[action].cast(self)
            self.taketurn(False, False, False, False)

        elif action == 'pass':
            return None

    def bot_triggers(self, whoseturn):
        ### Put any spell-specific BOT triggers here,
        ### like Inferno, which should set the global
        ### variables gameover = True and winner = self.enemy
        global gameover
        global winner

        if 'Inferno' in [spell.name[:-1] for spell in self.charged_spells]:
            jmessage(self.ws, "DEATH BY INFERNO!")
            jmessage(self.opp.ws, "DEATH BY INFERNO!")
            gameover = True
            winner = self.enemy


    def eot_triggers(self, whoseturn):
        ### Put code in here for every specific spell
        ### that causes eot triggers.
        ### It must come BEFORE the end-game code below!

        ### Check whether someone is up by 3 or more.

        ### Check whether the countdown == 0.
        global gameover
        global winner

        ### INSERT SPELL-SPECIFIC EOT EFFECTS HERE

        if 'Inferno' in [spell.name[:-1] for spell in self.charged_spells]:
            jmessage(self.ws, "INFERNO TRIGGER!")
            jmessage(self.opp.ws, "INFERNO TRIGGER!")
            for name in board.nodes:
                node = board.nodes[name]
                if node.stone == self.enemy:
                    for neighbor in node.neighbors:
                        if neighbor.stone == self.color:
                            node.stone = None
            board.update(True)




        ### END OF SPELL-SPECIFIC EOT EFFECTS

        redtotal = 0
        bluetotal = 1

        for name in self.board.nodes:
            color = self.board.nodes[name].stone
            if color == 'red':
                redtotal += 1
            elif color == 'blue':
                bluetotal += 1

        if redtotal > bluetotal + 2:
            gameover = True
            winner = 'red'

        elif bluetotal > redtotal + 2:
            gameover = True
            winner = 'blue'

        else:
            if self.board.countdown == 0:
                gameover = True
                if redtotal > bluetotal:
                    winner = 'red'
                elif bluetotal > redtotal:
                    winner = 'blue'
                else:
                    a = ['red', 'blue']
                    a.remove(whoseturn)
                    winner = a[0]

    def firstmove(self):
        jmessage(self.ws, "Where would you like to place your first stone? ", "node")

        while True:
            ingress = self.ws.receive()
            if json.loads(ingress)['message'] == 'ping':
                pong(self.ws)
                pong(self.opp.ws)
                continue
            else:
                break


        if json.loads(ingress)['message'] == 'reset':
                    raise resetException()
        nodename = json.loads(ingress)['message']




        node = self.board.nodes[nodename]
        if node.stone != None:
            jmessage(self.ws, "Invalid move-- your opponent started there!")
            self.firstmove()
            return None
        else:
            node.stone = self.color
            self.board.update()

            egress = {"type": "firstturnpass",}
            self.ws.send(json.dumps(egress))

            while True:
                while True:
                    ingress = self.ws.receive()
                    if json.loads(ingress)['message'] == 'ping':
                        pong(self.ws)
                        pong(self.opp.ws)
                        continue
                    else:
                        break


                if json.loads(ingress)['message'] == 'reset':
                    raise resetException()
                action = json.loads(ingress)['message']
                if action == "pass":
                    break



    def move(self, preloaded = False, standardmove = False, shadowing=False):
        ### If the user clicked on a node while they had 'move' action available,
        ### we call this move function with preloaded == the node they clicked.

        ### standardmove is True iff this is the player's standard move for the turn.
        if not preloaded:
            jmessage(self.ws, "Where would you like to move? ", "node")

            while True:
                ingress = self.ws.receive()
                if json.loads(ingress)['message'] == 'ping':
                    pong(self.ws)
                    pong(self.opp.ws)
                    continue
                else:
                    break

            if json.loads(ingress)['message'] == 'reset':
                    raise resetException()
            nodename = json.loads(ingress)['message']
        else:
            nodename = preloaded

        node = self.board.nodes[nodename]
        adjacent = False
        for neighbor in node.neighbors:
            if neighbor.stone == self.color:
                adjacent = True

        if node.stone == self.color:
            jmessage(self.ws, "Invalid move-- you already have a stone there!")
            self.move(standardmove=standardmove)
            return None

        elif not adjacent:
            if not (standardmove and ("Levity" in [spell.name[:-1] for spell in self.charged_spells])):
                jmessage(self.ws, "Invalid move-- that's not adjacent to you!")
                self.move(standardmove=standardmove)
                return None
            else:
                if node.stone == None:
                    node.stone = self.color
                    self.board.update()
                else:
                    jmessage(self.ws, "Invalid move-- Levity moves can only be into empty nodes!")
                    self.move(standardmove=standardmove)
                    return None


        elif node.stone == None:
            if shadowing:
                if node.name in ['a1', 'b1', 'c1']:
                    pass
                else:
                    locknodes = []
                    if red.lock != None:
                        locknodes += red.lock.position
                    if blue.lock != None:
                        locknodes += blue.lock.position

                    if node in locknodes:
                        pass
                    else:
                        jmessage(self.ws, "Invalid Shadow move")
                        self.move(shadowing=True)
                        return None

            node.stone = self.color
            self.board.update()

        elif node.stone == self.enemy:
            if shadowing:
                if node.name in ['a1', 'b1', 'c1']:
                    pass
                else:
                    locknodes = []
                    if red.lock != None:
                        locknodes += red.lock.position
                    if blue.lock != None:
                        locknodes += blue.lock.position

                    if node in locknodes:
                        pass
                    else:
                        jmessage(self.ws, "Invalid Shadow move")
                        self.move(shadowing=True)
                        return None
            self.pushenemy(node)



    def softmove(self):
        jmessage(self.ws, "Where would you like to soft move? ", "node")
        
        while True:
            ingress = self.ws.receive()
            if json.loads(ingress)['message'] == 'ping':
                pong(self.ws)
                pong(self.opp.ws)
                continue
            else:
                break


        if json.loads(ingress)['message'] == 'reset':
                    raise resetException()
        nodename = json.loads(ingress)['message']
        node = self.board.nodes[nodename]
        adjacent = False
        for neighbor in node.neighbors:
            if neighbor.stone == self.color:
                adjacent = True

        if node.stone == None and adjacent:
            node.stone = self.color
            self.board.update()

        elif node.stone == self.color:
            jmessage(self.ws, "Invalid move-- you already have a stone there!")
            self.softmove()
            return None

        elif not adjacent:
            jmessage(self.ws, "Invalid move-- that's not adjacent to you!")
            self.softmove()
            return None

        elif node.stone == self.enemy:
            jmessage(self.ws, "Invalid move-- that's not a soft move!")
            self.softmove()
            return None

    def hardmove(self):
        jmessage(self.ws, "Where would you like to hard move? ", "node")

        while True:
            ingress = self.ws.receive()
            if json.loads(ingress)['message'] == 'ping':
                pong(self.ws)
                pong(self.opp.ws)
                continue
            else:
                break

        if json.loads(ingress)['message'] == 'reset':
                    raise resetException()
        nodename = json.loads(ingress)['message']
        node = self.board.nodes[nodename]
        adjacent = False
        for neighbor in node.neighbors:
            if neighbor.stone == self.color:
                adjacent = True

        if not adjacent:
            jmessage(self.ws, "Invalid move-- that's not adjacent to you!")
            self.hardmove()
            return None

        elif node.stone == self.color:
            jmessage(self.ws, "Invalid move-- you already have a stone there!")
            self.hardmove()
            return None

        elif node.stone != self.enemy:
            jmessage(self.ws, "Invalid move-- that's not a hard move!")
            self.hardmove()
            return None

        else:
            self.pushenemy(node)

    def dash(self):
        if 'Nirvana' in [spell.name[:-1] for spell in self.charged_spells]:
            jmessage(self.ws, "Select your stone to sacrifice. ", "node")
            nirvana = True
        else:
            jmessage(self.ws, "Select your first stone to sacrifice. ", "node")
            nirvana = False
        
        while True:
            ingress = self.ws.receive()
            if json.loads(ingress)['message'] == 'ping':
                pong(self.ws)
                pong(self.opp.ws)
                continue
            else:
                break


        if json.loads(ingress)['message'] == 'reset':
                    raise resetException()
        sac1 = json.loads(ingress)['message']
        if self.board.nodes[sac1].stone != self.color:
            jmessage(self.ws, "You do not have a stone there!")
            self.dash()
            return None

        self.board.nodes[sac1].stone = None
        self.board.update()

        if not nirvana:
            while True:
                jmessage(self.ws, "Select your second stone to sacrifice. ", "node")
                

                while True:
                    ingress = self.ws.receive()
                    if json.loads(ingress)['message'] == 'ping':
                        pong(self.ws)
                        pong(self.opp.ws)
                        continue
                    else:
                        break



                if json.loads(ingress)['message'] == 'reset':
                        raise resetException()
                sac2 = json.loads(ingress)['message']
                if (self.board.nodes[sac2].stone != self.color):
                    jmessage(self.ws, "You do not have a stone there!")
                    continue
                else:
                    break
        
            self.board.nodes[sac2].stone = None
            self.board.update()
            
        self.move()

        ### Update the new score
        self.board.update(True)

    def pushenemy(self, node):
        node.stone = self.color
        self.board.update()
        ### push the enemy stone. Return a list of options
        ### for where to push it.
        pushingqueue = [(x, 1) for x in node.neighbors]
        pushingoptions = []
        alreadyvisited = [node]
        ### This loop searches for a first valid pushing option
        while pushingoptions == []:
            if pushingqueue == []:
                jmessage(self.ws, "Enemy stone crushed!")
                self.board.update()
                return None
            nextpair = pushingqueue.pop(0)
            nextnode, distance = nextpair
            alreadyvisited.append(nextnode)
            if nextnode.stone == self.color:
                continue
            elif nextnode.stone == self.enemy:
                for neighbor in nextnode.neighbors:
                    if neighbor not in alreadyvisited:
                        pushingqueue.append((neighbor, distance + 1))
                continue
            else:
                pushingoptions.append(nextnode)
                shortestdistance = distance

        ### This loop finishes finding the other pushing options
        ### at the same distance, and breaks when distance gets bigger
        while pushingqueue != []:
            nextpair = pushingqueue.pop(0)
            nextnode, distance = nextpair
            if distance > shortestdistance:
                break
            if nextnode.stone == None:
                pushingoptions.append(nextnode)

        pushingoptionnames = [x.name for x in pushingoptions]

        if len(pushingoptionnames) == 1:
            self.board.nodes[pushingoptionnames[0]].stone = self.enemy
            self.board.update()
            return None

        while True:
            egress = {"type": "pushingoptions", }
            for nodename in pushingoptionnames:
                egress[nodename] = self.enemy

            self.ws.send(json.dumps(egress))

            jmessage(self.ws, "Where would you like to push the enemy stone? ", "node")
            

            while True:
                ingress = self.ws.receive()
                if json.loads(ingress)['message'] == 'ping':
                    pong(self.ws)
                    pong(self.opp.ws)
                    continue
                else:
                    break



            if json.loads(ingress)['message'] == 'reset':
                    raise resetException()
            push = json.loads(ingress)['message']
            if push not in pushingoptionnames:
                jmessage(self.ws, "Invalid option!")
                continue
            self.board.nodes[push].stone = self.enemy
            self.board.update()
            jmessage(self.ws, "Enemy stone pushed to " + push)
            break


##############  GAME LOOP  ##############

### First we set up the objects.  This is my hack-y way of passing
### everyone as parameters to everyone else: doing it
### in two layers, using the board.addplayers method



def pong(playerwebsocket):
    egress =  {"type": "pong"}
    playerwebsocket.send(json.dumps(egress))


def jmessage(playerwebsocket, message, awaiting= None):
    ### The 'playerwebsocket' parameter here is not a player object,
    ### but rather player.ws
    egress =  {"type": "message", "message": message, "awaiting": awaiting, }
    playerwebsocket.send(json.dumps(egress))


class resetException(Exception):
    pass

board = Board()
red = Player(board, 'red')
blue = Player(board, 'blue')
board.addplayers(red, blue)
red.opp = blue
blue.opp = red

turncounter = 3
whoseturn = None
currentplayerhasmoved = False
gameover = False
winner = None

app = Flask(__name__)
sockets = Sockets(app)

totalplayers = 0
whoisred = randint(1,2)
whoisblue = 3 - whoisred
redjoined = False
bluejoined = False


# The first player to join will be red.


@sockets.route('/api/game')
def playgame(ws):
    global totalplayers
    global redjoined
    global bluejoined
    global turncounter
    global whoseturn
    global currentplayerhasmoved
    global gameover
    global winner
    totalplayers += 1
    if totalplayers == whoisred:
        red.ws = ws
        jmessage(red.ws, "You are RED this game.")


        ### spellsetup is a JSON dictionary with keys "major2", "charm3", etc.,
        ### and values "Flourish2", "Sprout3", etc.
        egress = { "type": "spellsetup" }

        egress["major1"] = board.spells[0].name
        egress["major2"] = board.spells[1].name
        egress["major3"] = board.spells[2].name
        egress["minor1"] = board.spells[3].name
        egress["minor2"] = board.spells[4].name
        egress["minor3"] = board.spells[5].name
        egress["charm1"] = board.spells[6].name
        egress["charm2"] = board.spells[7].name
        egress["charm3"] = board.spells[8].name
        
        red.ws.send(json.dumps(egress))

        egress = { "type": "spelltextsetup" }

        egress["major1"] = board.spells[0].text
        egress["major2"] = board.spells[1].text
        egress["major3"] = board.spells[2].text
        egress["minor1"] = board.spells[3].text
        egress["minor2"] = board.spells[4].text
        egress["minor3"] = board.spells[5].text
        egress["charm1"] = board.spells[6].text
        egress["charm2"] = board.spells[7].text
        egress["charm3"] = board.spells[8].text
        
        red.ws.send(json.dumps(egress))

        while True:
            ingress = red.ws.receive()
            message = json.loads(ingress)['message']
            if message == 'ping':
                pong(red.ws)
                continue
            elif message == 'joinedgame':
                redjoined = True
                break
                
        if not bluejoined:
            jmessage(red.ws, "Waiting for opponent to join...")
        while True:
            pong(red.ws)
            gevent.sleep(3)


    elif totalplayers == whoisblue:
        blue.ws = ws
        jmessage(blue.ws,"You are BLUE this game.")


        ### spellsetup is a JSON dictionary with keys "major2", "charm3", etc.,
        ### and values "Flourish2", "Sprout3", etc.
        egress = { "type": "spellsetup" }

        egress["major1"] = board.spells[0].name
        egress["major2"] = board.spells[1].name
        egress["major3"] = board.spells[2].name
        egress["minor1"] = board.spells[3].name
        egress["minor2"] = board.spells[4].name
        egress["minor3"] = board.spells[5].name
        egress["charm1"] = board.spells[6].name
        egress["charm2"] = board.spells[7].name
        egress["charm3"] = board.spells[8].name
        
        blue.ws.send(json.dumps(egress))


        egress = { "type": "spelltextsetup" }

        egress["major1"] = board.spells[0].text
        egress["major2"] = board.spells[1].text
        egress["major3"] = board.spells[2].text
        egress["minor1"] = board.spells[3].text
        egress["minor2"] = board.spells[4].text
        egress["minor3"] = board.spells[5].text
        egress["charm1"] = board.spells[6].text
        egress["charm2"] = board.spells[7].text
        egress["charm3"] = board.spells[8].text
        
        blue.ws.send(json.dumps(egress))

        while True:
            ingress = blue.ws.receive()
            message = json.loads(ingress)['message']
            if message == 'ping':
                pong(blue.ws)
                continue
            elif message == 'joinedgame':
                bluejoined = True
                break
        alreadymessaged = False
        while True:
            if redjoined:
                break
            else:
                if not alreadymessaged:
                    jmessage(blue.ws, "Waiting for opponent to join...")
                    alreadymessaged = True
                gevent.sleep(.1)



        jmessage(red.ws,"Ready to play!")
        jmessage(blue.ws,"Ready to play!")
        time.sleep(3)

        board.take_snapshot()

        egress = { "type": "whoseturndisplay", "color": 'red', 
            "message": "Red Turn 1" }
        red.ws.send(json.dumps(egress))
        blue.ws.send(json.dumps(egress))

        while True:
            try:
                jmessage(red.ws,"\nRed Turn 1")
                whoseturn = 'red'
                red.firstmove()
                break

            except resetException:
                ### Reset all attributes of the game & board
                ### to the way they were in board.snapshot , 
                ### then we restart the turn loop.
                jmessage(red.ws, "Resetting Turn")
                jmessage(blue.ws, "Resetting Turn")

                for nodename in board.nodes:
                    board.nodes[nodename].stone = board.snapshot[nodename]

                board.update()
                continue

        board.take_snapshot()

        egress = { "type": "whoseturndisplay", "color": 'blue', 
            "message": "Blue Turn 1" }
        red.ws.send(json.dumps(egress))
        blue.ws.send(json.dumps(egress))

        while True:
            try:
                jmessage(blue.ws,"\nBlue Turn 1")
                whoseturn = 'blue'
                blue.firstmove()
                break
            except resetException:
                jmessage(red.ws, "Resetting Turn")
                jmessage(blue.ws, "Resetting Turn")

                for nodename in board.nodes:
                    board.nodes[nodename].stone = board.snapshot[nodename]

                board.update()
                continue



        while True:
            ### First take a snapshot of the board,
            ### which we will revert to in case of a reset exception.
            
            board.take_snapshot()

            turncounter += 1
            currentplayerhasmoved = False

            if turncounter % 2 == 0:
                activeplayer = red
                whoseturn = 'red'
            else:
                activeplayer = blue
                whoseturn = 'blue'

            
            try:
                board.display(whoseturn)
                if whoseturn == 'red':
                    message = "Red Turn " + str(turncounter // 2)
                elif whoseturn == 'blue':
                    message = "Blue Turn " + str(turncounter // 2)

                egress = { "type": "whoseturndisplay", "color": whoseturn, "message": message }
                red.ws.send(json.dumps(egress))
                blue.ws.send(json.dumps(egress))

                activeplayer.bot_triggers(whoseturn)
                if gameover:
                    board.end_game(winner)
                    break

                if whoseturn == 'red':
                    jmessage(red.ws,"\nRed Turn " + str(turncounter // 2))
                    red.taketurn()
                else:
                    jmessage(blue.ws,"\nBlue Turn " + str(turncounter // 2))
                    blue.taketurn()

                activeplayer.eot_triggers(whoseturn)
                if gameover:
                    board.end_game(winner)
                    break

            except resetException:
                ### Reset all attributes of the game & board
                ### to the way they were in board.snapshot , 
                ### then we restart the turn loop.
                jmessage(red.ws, "Resetting Turn")
                jmessage(blue.ws, "Resetting Turn")

                snapshot = board.snapshot

                turncounter = snapshot["turncounter"]
                currentplayerhasmoved = snapshot["currentplayerhasmoved"]
                gameover = snapshot["gameover"]
                winner = snapshot["winner"]
                board.score = snapshot["score"]



                for nodename in board.nodes:
                    board.nodes[nodename].stone = snapshot[nodename]
                if snapshot["redlock"]:
                    red.lock = board.spelldict[snapshot["redlock"]]
                else:
                    red.lock = None
                
                if snapshot["bluelock"]:
                    blue.lock = board.spelldict[snapshot["bluelock"]]
                else:
                    blue.lock = None

                board.countdown = snapshot["countdown"]

                board.update(True)

                continue




totalchatters = 0
redchatws = None
bluechatws = None

@sockets.route('/api/chat')
def chat(ws):

    global totalchatters
    global redchatws
    global bluechatws
    totalchatters += 1
    if totalchatters == 1:
        redchatws = ws
        while True:
            ingress = redchatws.receive()
            message = json.loads(ingress)['message']
            if message == "ping":
                pong(redchatws)
                continue
            else:
                egress = {"type": "chatmessage", "player": "Red:", "message": message }
                redchatws.send(json.dumps(egress))
                if totalchatters == 2:
                    bluechatws.send(json.dumps(egress))

                
            

    elif totalchatters == 2:
        bluechatws = ws
        while True:
            ingress = bluechatws.receive()
            message = json.loads(ingress)['message']

            if message == "ping":
                pong(bluechatws)
                continue

            else:
                egress = {"type": "chatmessage", "player": "Blue:", "message": message }
                
                redchatws.send(json.dumps(egress))
                bluechatws.send(json.dumps(egress))








