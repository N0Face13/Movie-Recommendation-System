import requests
import folium

# Geoapify API Key
API_KEY = '51b7c39712234931a7d803869b59867c'  # Replace with your actual Geoapify API key

def fetch_route(start_coords, end_coords):
    """Fetch the route from Geoapify API."""
    # Prepare the URL with waypoints for the request
    waypoints = f"{start_coords[0]},{start_coords[1]}|{end_coords[0]},{end_coords[1]}"
    url = f"https://api.geoapify.com/v1/routing?waypoints={waypoints}&mode=drive&apiKey={API_KEY}"

    # Make the API request
    response = requests.get(url)

    # Debugging output for response status
    print(f"Fetching route from {start_coords} to {end_coords}...")
    print(f"Request URL: {url}")
    print(f"Response Status Code: {response.status_code}")  # Print the status code

    if response.status_code == 200:
        route_data = response.json()
        print("Route Data:", route_data)  # Print the route data to check its structure
        
        if 'features' in route_data and len(route_data['features']) > 0:
            # Extract the geometry type and coordinates of the route
            geometry_type = route_data['features'][0]['geometry']['type']
            route_coords = route_data['features'][0]['geometry']['coordinates']
            routeTotalTimeSeconds = route_data['features'][0]['properties']['time']
            
            print(f"Geometry Type: {geometry_type}")  # Print geometry type for debugging
            print(f"Route Coordinates: {route_coords}")  # Print coordinates to see structure
            print(f"Total time for the route: {routeTotalTimeSeconds} seconds")  # Print total time

            # Handle different geometry types (LineString or MultiLineString)
            if geometry_type == "LineString":
                # Single route path
                route_lat_lon = [(coord[1], coord[0]) for coord in route_coords]
                return route_lat_lon, routeTotalTimeSeconds

            elif geometry_type == "MultiLineString":
                # Multiple route segments (combine them into one path)
                route_lat_lon = []
                for segment in route_coords:
                    route_lat_lon.extend([(coord[1], coord[0]) for coord in segment])
                return route_lat_lon, routeTotalTimeSeconds

        else:
            print("No route found in the response.")
            return None, None
    else:
        print(f"Error fetching route: {response.status_code} {response.text}")
        return None, None

def create_map(start_coords, end_coords, route):
    """Create a map with markers and route."""
    # Create a Folium map centered around the start location
    map = folium.Map(location=start_coords, zoom_start=14)

    # Markers for start and end locations
    folium.Marker(location=start_coords, popup='Start: Burj Khalifa', icon=folium.Icon(color='green')).add_to(map)
    folium.Marker(location=end_coords, popup='End: JLT', icon=folium.Icon(color='red')).add_to(map)

    # Add route to map if it exists
    if route:
        folium.PolyLine(route, color='blue', weight=5, opacity=0.7).add_to(map)
        print("Route added to map.")  # Debugging statement
    else:
        print("No route to add to the map.")

    # Save map to HTML file
    map.save('route_map.html')
    print("Map saved as route_map.html")

def main():
    # Start and end coordinates
    start_coords = (25.197033599999997, 55.27413294647308)  # Burj Khalifa
    end_coords = (25.0722, 55.1446)  # JLT

    # Fetch the route
    route, route_time = fetch_route(start_coords, end_coords)

    # Create and save the map
    create_map(start_coords, end_coords, route)

    # Print the total time for the route
    if route_time is not None:
        print(f"Total travel time: {route_time} seconds")

if __name__ == "__main__":
    main()
