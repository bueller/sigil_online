
### Sigil Online spell file
### To play "All-Green", un-comment the last line at the bottom of file


import random


### FULL MAJOR LIST: Flourish, Onlsaught, Bewitch, Syzygy, Nirvana, Inferno

### FULL MINOR LIST: Grow, Fury, Fire, Ice, Thunder, Levity

### FULL CHARM LIST: Sprout, Stomp, Gust, Blink


allmajorspells = [ 'Flourish', 'Onslaught', 'Bewitch', 'Syzygy',]

allminorspells = [ 'Grow', 'Fury', 'Fire', 'Ice',]

allcharms = ['Sprout', 'Stomp', 'Gust', 'Blink']


majorspells = random.sample(allmajorspells, 3)
minorspells = random.sample(allminorspells, 3)
charms = random.sample(allcharms, 3)

major1 = majorspells[0] + "(self, self.positions[1], '" + majorspells[0] + "1')"

major2 = majorspells[1] + "(self, self.positions[2], '" + majorspells[1] + "2')"

major3 = majorspells[2] + "(self, self.positions[3], '" + majorspells[2] + "3')"


minor1 = minorspells[0] + "(self, self.positions[4], '" + minorspells[0] + "1')"

minor2 = minorspells[1] + "(self, self.positions[5], '" + minorspells[1] + "2')"

minor3 = minorspells[2] + "(self, self.positions[6], '" + minorspells[2] + "3')"


charm1 = charms[0] + "(self, self.positions[7], '" + charms[0] + "1')"

charm2 = charms[1] + "(self, self.positions[8], '" + charms[1] + "2')"

charm3 = charms[2] + "(self, self.positions[9], '" + charms[2] + "3')"



spell_list = [major1, major2, major3, minor1, minor2, minor3, charm1, charm2, charm3]


### should be a list of strings, which will turn into the spell objects
### when we hit them with eval()

### MUST BE READY TO INSTANTIATE when we eval() them!

### To instantiate a spell, it needs the following parameters:

### (board, position, name)

### We will be instantiating these spell objects as a method
### inside the board object.  So the 'board' parameter
### should be written as 'self'.  The 'position' parameter
### should be written as 'self.positions[i]' for the i-th spell.
### Then 'name' can be a string.

all_green1 = "Flourish(self, self.positions[1], 'Flourish1')"

all_green2 = "Flourish(self, self.positions[2], 'Flourish2')"

all_green3 = "Flourish(self, self.positions[3], 'Flourish3')"

all_green4 = "Grow(self, self.positions[4], 'Grow1')"

all_green5 = "Grow(self, self.positions[5], 'Grow2')"

all_green6 = "Grow(self, self.positions[6], 'Grow3')"

all_green7 = "Sprout(self, self.positions[7], 'Sprout1')"

all_green8 = "Sprout(self, self.positions[8], 'Sprout2')"

all_green9 = "Sprout(self, self.positions[9], 'Sprout3')"


### UNCOMMENT THE LINE BELOW TO PLAY ALL-GREEN

#spell_list = [all_green1, all_green2, all_green3, all_green4, all_green5, all_green6, all_green7, all_green8, all_green9]








