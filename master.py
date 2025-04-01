from map import Map
from ans import ANS
import drive

# Build Map
map = Map("locations.csv", "routes.csv")

# Get turn sequence
attributr_weights = {"distance":1,"speed":1,"traffic":1}
ans = ANS(map,attributr_weights)
turns = ans.get_turn_sequence("R2",(38,10))

# Excecute
drive.drive(turns)



