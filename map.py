import networkx as nx
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



class Map:

    def __init__(self,locations_file_path,routes_file_path):
        self._G = nx.DiGraph()
        self.add_locations(locations_file_path)
        self.add_routes(routes_file_path)
        

    def copy_map(self):
        new_map = Map()
        new_map._G = self._G.copy()
        return new_map

    def add_location(self, location, x=None, y=None):
        if location not in self._G:
            self._G.add_node(location, x=x, y=y)
        else:
            current_data = self._G.nodes[location]
            if x is not None:
                current_data['x'] = x
            if y is not None:
                current_data['y'] = y

    def remove_location(self, location):
        if location in self._G:
            self._G.remove_node(location)

    def add_route(self, loc1, loc2, **attributes):
        if loc1 not in self._G:
            self.add_location(loc1)
        if loc2 not in self._G:
            self.add_location(loc2)
        self._G.add_edge(loc1, loc2, **attributes)

    def remove_route(self, loc1, loc2):
        if self._G.has_edge(loc1, loc2):
            self._G.remove_edge(loc1, loc2)

    def add_locations(self,locations_file_path):
        locations_df = pd.read_csv(locations_file_path)
        locations = {row[0]: tuple(map(int, row[1].split(','))) for _, row in locations_df.iterrows()}        
        for name, (x, y) in locations.items():
            self.add_location(name, x=x, y=y)

    def add_routes(self,routes_file_path):
        routes_df = pd.read_csv(routes_file_path)    
        routes = {row[0]: tuple(row[1].replace(" ", "").split(',')) for index, row in routes_df.iterrows()}
        attributes = routes_df.iloc[:, 2:].to_dict(orient='records')
        for (name, (s, f)), attrs in zip(routes.items(), attributes):
            if s in self._G and f in self._G:
                self.add_route(s, f, route_name=name, **attrs)
            else:
                print(f"Warning: Route {name} contains undefined locations: {s}, {f}")
        

    def shortest_path(self, start, end, attr_weights):

        if start not in self._G or end not in self._G:
            return None, float('inf')

        def edge_cost(u, v, data):
            cost = 0
            for attr_name, weight_factor in attr_weights.items():
                if attr_name not in data:
                    raise ValueError(f"Edge from {u} to {v} is missing required attribute '{attr_name}'")
                cost += data[attr_name] * weight_factor
            return cost

        try:
            path = nx.shortest_path(self._G, source=start, target=end, weight=edge_cost)
            total_cost = nx.shortest_path_length(self._G, source=start, target=end, weight=edge_cost)
            return path, total_cost
        except nx.NetworkXNoPath:
            return None, float('inf')
        

    def find_nearest_edge_destination(self, x, y):
        """
        Given an (x, y) coordinate, find the closest edge in the directed graph
        and return the destination node of that edge.
        """
        if not self._G.edges:
            raise ValueError("No edges exist in the map.")

        closest_edge = None
        min_distance = float('inf')

        for u, v, data in self._G.edges(data=True):
            x_u, y_u = self._G.nodes[u].get('x'), self._G.nodes[u].get('y')
            x_v, y_v = self._G.nodes[v].get('x'), self._G.nodes[v].get('y')

            if x_u is None or y_u is None or x_v is None or y_v is None:
                continue  # Skip edges with missing coordinates

            # Compute the closest point on the segment (u, v) to (x, y)
            ux, uy = x_v - x_u, y_v - y_u
            vx, vy = x - x_u, y - y_u

            # Compute projection scalar
            t = (vx * ux + vy * uy) / (ux ** 2 + uy ** 2) if (ux ** 2 + uy ** 2) > 0 else 0
            t = max(0, min(1, t))  # Clamp t to stay within the segment

            closest_x, closest_y = x_u + t * ux, y_u + t * uy
            distance = np.hypot(closest_x - x, closest_y - y)

            if distance < min_distance:
                min_distance = distance
                closest_edge = (u, v)

        if closest_edge is None:
            raise ValueError("No valid edges found with proper coordinates.")

        # Return the destination node of the closest edge
        return closest_edge[1]

    def visualize_map(self, path=None, title="Map Visualization"):
        pos = {}
        for node, data in self._G.nodes(data=True):
            x = data.get('x')
            y = data.get('y')
            if x is None or y is None:
                raise ValueError(f"Node '{node}' does not have x,y coordinates.")
            pos[node] = (x, y)

        # Set the figure size
        plt.figure(figsize=(20,20))
        # Draw nodes and edges
        nx.draw_networkx_nodes(self._G, pos, node_size=800, node_color='lightblue')
        nx.draw_networkx_edges(self._G, pos, arrowstyle='->', arrowsize=20) #added arrowstyle and arrowsize
        nx.draw_networkx_labels(self._G, pos, font_size=10, font_color='black')

        # If a path is specified, highlight it
        if path and len(path) > 1:
            path_edges = list(zip(path, path[1:]))
            nx.draw_networkx_edges(
                self._G, pos,
                edgelist=path_edges,
                edge_color='red',
                width=2,
                arrowstyle='->', #added arrowstyle
                arrowsize=20 #added arrowsize
            )
        
        plt.title(title)
        plt.axis('equal')  # Keep the aspect ratio
        plt.show()

    def generate_coordinates(self):
        """
        Randomly pick one existing edge (u, v). Then choose a random point on the
        line segment between them and return (x, y, u, v).
        """
        edges_list = list(self._G.edges(data=True))
        if not edges_list:
            raise ValueError("No edges exist in the map. Cannot generate a coordinate.")

        u, v, data = random.choice(edges_list)

        x_u = self._G.nodes[u].get('x')
        y_u = self._G.nodes[u].get('y')
        x_v = self._G.nodes[v].get('x')
        y_v = self._G.nodes[v].get('y')

        if x_u is None or y_u is None or x_v is None or y_v is None:
            raise ValueError(f"Edge from {u} to {v} has missing node coordinates.")

        t = random.random()
        x = x_u + t * (x_v - x_u)
        y = y_u + t * (y_v - y_u)

        return x, y, u, v

    def add_coordinates(self, new_node, x, y, u, v):
        """
        Insert a new node with coordinates (x, y) between two existing nodes u and v.
        The original edge (u, v) is removed. Two new edges:
            (u, new_node) and (new_node, v)
        are created with the same attributes as (u, v).
        """
        if not self._G.has_edge(u, v):
            raise ValueError(f"No edge found between {u} and {v}.")

        # Copy the original edge's attributes
        original_data = dict(self._G[u][v])

        # Remove the original edge
        self.remove_route(u, v)

        # Create the new node
        self.add_location(new_node, x, y)

        # Add edges (u, new_node) and (new_node, v) with the same attributes
        self.add_route(u, new_node, **original_data)
        self.add_route(new_node, v, **original_data)

    def __str__(self):
        return nx.info(self._G)
    
    
