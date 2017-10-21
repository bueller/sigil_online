### Sigil Online spell file












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

s1 = "Flourish(self, self.positions[1], 'Flourish1')"

s2 = "Flourish(self, self.positions[2], 'Flourish2')"

s3 = "Flourish(self, self.positions[3], 'Flourish3')"

s4 = "Grow(self, self.positions[4], 'Grow1')"

s5 = "Grow(self, self.positions[5], 'Grow2')"

s6 = "Grow(self, self.positions[6], 'Grow3')"

s7 = "Sprout(self, self.positions[7], 'Sprout1')"

s8 = "Sprout(self, self.positions[8], 'Sprout2')"

s9 = "Sprout(self, self.positions[9], 'Sprout3')"




spell_list = [s1, s2, s3, s4, s5, s6, s7, s8, s9]











