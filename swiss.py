from pypair import Tournament

Players = { 1:"Tim",
            2:"Jeff",
            3:"Kristi",
            4:"Jacob",
            5:"Doug",
            6:"Karen",
            7:"David", 
            8:"Josh"}

to = Tournament()

for player in Players:
    to.addPlayer( player, Players[player] )
pairings1 = to.pairRound()
for table in pairings1:
    to.reportMatch(table, [1,1,1])
pairings2 = to.pairRound()
for table in pairings2:
    to.reportMatch(table, [1,1,1])



print(pairings1)
print(pairings2)
