class ANS:
 
 def __init__(self,map,attribute_weights):
     self.map = map
     self.attribute_weights = attribute_weights
     
 def get_turn_sequence(self,upcoming_intersection,destination_coordinates):
    

    start_node = list(self.map._G.predecessors(upcoming_intersection))[0]
    end_node = self.map.find_nearest_edge_destination(destination_coordinates[0],destination_coordinates[1])
    path, total_cost = self.map.shortest_path(start_node, end_node, self.attribute_weights)


    if len(path) < 3:
        raise ValueError("At least three locations are needed to determine turns.")

    turns = []
    
    for i in range(len(path) - 2):
        loc1, loc2, loc3 = path[i], path[i+1], path[i+2]

        # Get coordinates of the three consecutive points
        x1, y1 = self.map._G.nodes[loc1].get('x'), self.map._G.nodes[loc1].get('y')
        x2, y2 = self.map._G.nodes[loc2].get('x'), self.map._G.nodes[loc2].get('y')
        x3, y3 = self.map._G.nodes[loc3].get('x'), self.map._G.nodes[loc3].get('y')

        if None in (x1, y1, x2, y2, x3, y3):
            raise ValueError(f"One or more locations do not have valid coordinates: {loc1}, {loc2}, {loc3}")

        # Compute the cross product to determine turn direction
        vector1 = (x2 - x1, y2 - y1)  # Vector from loc1 to loc2
        vector2 = (x3 - x2, y3 - y2)  # Vector from loc2 to loc3

        cross_product = vector1[0] * vector2[1] - vector1[1] * vector2[0]

        if cross_product > 0:
            turns.append("left")
        elif cross_product < 0:
            turns.append("right")
        else:
            turns.append("straight")

    return turns
 
 