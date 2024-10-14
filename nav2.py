import osmnx as ox
import networkx as nx
import folium

def visualize_nearest_nodes(G, start_coords, end_coords):
    """Visualize the nearest nodes on the graph for debugging."""
    start_node = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
    end_node = ox.distance.nearest_nodes(G, end_coords[1], end_coords[0])
    
    start_node_coords = (G.nodes[start_node]['y'], G.nodes[start_node]['x'])
    end_node_coords = (G.nodes[end_node]['y'], G.nodes[end_node]['x'])
    
    print(f"Start Node Coordinates: {start_node_coords}")
    print(f"End Node Coordinates: {end_node_coords}")

    # Create a map to visualize nodes
    map = folium.Map(location=start_coords, zoom_start=14)
    folium.Marker(location=start_coords, popup='Start', icon=folium.Icon(color='green')).add_to(map)
    folium.Marker(location=end_coords, popup='End', icon=folium.Icon(color='red')).add_to(map)
    folium.Marker(location=start_node_coords, popup='Start Node', icon=folium.Icon(color='blue')).add_to(map)
    folium.Marker(location=end_node_coords, popup='End Node', icon=folium.Icon(color='purple')).add_to(map)

    # Save the debug map to visualize the nodes
    map.save('debug_map.html')
    print("Debug map saved as debug_map.html")

def dijkstra_shortest_path(G, start_coords, end_coords):
    """Find the shortest path between two coordinates using Dijkstra's Algorithm."""
    # Find the nearest nodes on the graph to the start and end points
    start_node = ox.distance.nearest_nodes(G, start_coords[1], start_coords[0])
    end_node = ox.distance.nearest_nodes(G, end_coords[1], end_coords[0])

    print(f"Start Coordinates: {start_coords} -> Nearest Node: {start_node}")
    print(f"End Coordinates: {end_coords} -> Nearest Node: {end_node}")

    if start_node == end_node:
        print("Error: Start and End nodes are the same. Please check the coordinates.")
        return None, 0  # No route if nodes are the same

    # Use NetworkX's built-in Dijkstra's algorithm to find the shortest path
    shortest_path = nx.shortest_path(G, start_node, end_node, weight='length')

    # Convert node IDs back to lat-lon coordinates
    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in shortest_path]

    # Calculate the total distance of the route in meters
    total_distance = sum(
        G.edges[shortest_path[i], shortest_path[i + 1]]['length']
        for i in range(len(shortest_path) - 1)
    )

    return route_coords, total_distance

def create_map(start_coords, end_coords, route):
    """Create a map with markers and route using Folium."""
    # Create a Folium map centered around the start location
    map = folium.Map(location=start_coords, zoom_start=14)

    # Markers for start and end locations
    folium.Marker(location=start_coords, popup='Start', icon=folium.Icon(color='green')).add_to(map)
    folium.Marker(location=end_coords, popup='End', icon=folium.Icon(color='red')).add_to(map)

    # Add the route to the map
    if route:
        folium.PolyLine(route, color='blue', weight=5, opacity=0.7).add_to(map)
        print("Route added to the map.")  # Debugging statement

    # Save the map to an HTML file
    map.save('route_map.html')
    print("Map saved as route_map.html")

def main():
    # Start and end coordinates (adjust these coordinates if necessary)
    start_coords = (25.197, 55.274)  # Burj Khalifa
    end_coords = (25.203, 55.388)  # Adjust as needed

    print("Fetching the road network...")
    # Limit the area by using a bounding box instead of the entire Dubai region
    north, south, east, west = 25.3, 25.1, 55.4, 55.2  # Adjust this bounding box as needed
    G = ox.graph_from_bbox(north, south, east, west, network_type='drive')

    # Project the graph to UTM (this makes spatial operations more accurate and efficient)
    G = ox.project_graph(G)

    print("Road network fetched and projected successfully!")

    # Visualize the nearest nodes for debugging
    visualize_nearest_nodes(G, start_coords, end_coords)

    # Find the shortest path using Dijkstra's algorithm
    print("Finding shortest path...")
    route, total_distance = dijkstra_shortest_path(G, start_coords, end_coords)

    if route is None:
        print("No valid route found. Exiting.")
        return

    print("Route found. Now generating the map...")

    # Calculate travel time (in seconds) assuming an average driving speed of 50 km/h
    average_speed_kmh = 50  # Average speed in km/h
    average_speed_ms = average_speed_kmh * (1000 / 3600)  # Convert to m/s
    travel_time_seconds = total_distance / average_speed_ms  # Total travel time in seconds

    # Print the total distance and travel time
    print(f"Total distance: {total_distance:.2f} meters")
    print(f"Estimated travel time: {travel_time_seconds:.2f} seconds")

    # Create and save the map with the route
    create_map(start_coords, end_coords, route)

if __name__ == "__main__":
    main()
