import osmnx as ox
import networkx as nx
import folium

def dijkstra_shortest_path(G, start_coords, end_coords):
    """Find the shortest path between two coordinates using Dijkstra's Algorithm."""
    start_node = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
    end_node = ox.distance.nearest_nodes(G, end_coords[1], end_coords[0])
    print(f"Start Node: {start_node}, End Node: {end_node}")

    if start_node == end_node:
        print("Start and end nodes are the same. Please choose different start and end points.")
        return None, 0

    shortest_path = nx.shortest_path(G, start_node, end_node, weight='length')
    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]
    total_distance = sum(
        G.edges[shortest_path[i], shortest_path[i + 1]]['length']
        for i in range(len(shortest_path) - 1)
    )
    return route_coords, total_distance

def create_map(start_coords, end_coords, route):
    """Create a map with markers and route using Folium."""
    map_center = [(start_coords[0] + end_coords[0]) / 2, (start_coords[1] + end_coords[1]) / 2]
    map = folium.Map(location=map_center, zoom_start=12)
    folium.Marker(location=start_coords, popup='Start', icon=folium.Icon(color='green')).add_to(map)
    folium.Marker(location=end_coords, popup='End', icon=folium.Icon(color='red')).add_to(map)
    if route:
        folium.PolyLine(route, color='blue', weight=5, opacity=0.7).add_to(map)
        print("Route added to the map.")
    map.save('route_map.html')
    print("Map saved as route_map.html")

def main():
    # Specific coordinates within New Delhi
    start_coords = (28.6139, 77.2090)  # India Gate, New Delhi
    end_coords = (28.5245, 77.1855)    # Qutub Minar, New Delhi

    print("Fetching the road network...")
    try:
        north, south, east, west = 28.65, 28.50, 77.25, 77.10
        G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
        G = ox.project_graph(G)
        print("Road network fetched and projected successfully!")
    except Exception as e:
        print(f"Error fetching road network: {e}")
        return

    # Check if coordinates are within bounds
    if not (south <= start_coords[0] <= north and west <= start_coords[1] <= east):
        print("Start coordinates are out of bounds.")
        return
    if not (south <= end_coords[0] <= north and west <= end_coords[1] <= east):
        print("End coordinates are out of bounds.")
        return

    try:
        start_node = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
        end_node = ox.distance.nearest_nodes(G, end_coords[1], end_coords[0])
        print(f"Checked Start Node: {start_node}, Checked End Node: {end_node}")
    except Exception as e:
        print(f"Error finding nearest nodes: {e}")
        return

    # Let's print some more detail about these nodes to investigate
    try:
        start_node_data = G.nodes[start_node]
        end_node_data = G.nodes[end_node]
        print(f"Start Node Data: {start_node_data}")
        print(f"End Node Data: {end_node_data}")
    except Exception as e:
        print(f"Error fetching node data: {e}")
        return

    if start_node == end_node:
        print("Start and end nodes are the same. Please choose different start and end points.")
        return

    print("Finding shortest path...")
    try:
        route, total_distance = dijkstra_shortest_path(G, start_coords, end_coords)
    except Exception as e:
        print(f"Error finding shortest path: {e}")
        return

    if route:
        print("Route found. Now generating the map...")
        average_speed_kmh = 50
        average_speed_ms = average_speed_kmh * (1000 / 3600)
        travel_time_seconds = total_distance / average_speed_ms
        print(f"Total distance: {total_distance:.2f} meters")
        print(f"Estimated travel time: {travel_time_seconds:.2f} seconds")
        create_map(start_coords, end_coords, route)
    else:
        print("Failed to find a route between the start and end points.")

if __name__ == "__main__":
    main()
