import json
import math

def readMap(mapFilename):
    with open(mapFilename + ".json") as f:
        mapData = json.load(f)
    with open(mapFilename + "_meta.json") as f:
        meta = json.load(f)
    return mapData, meta

def relative_wind_angle(boat_dir, wind_dir):
    """Calculate relative angle between boat heading and wind-from direction"""
    # Wind blows TO wind_dir, so wind comes FROM wind_dir + 180
    wind_from = (wind_dir + 180) % 360
    
    # Calculate angle between boat heading and wind-from
    diff = abs(boat_dir - wind_from)
    rel = min(diff, 360 - diff)
    return rel

# Map vectors to their corresponding headings and compass names
# These must match the MATLAB game exactly!
ALLOWED_MOVES = {
    0:   ([-1, 0],  "N"),   # North
    60:  ([-1, 1],  "NE"),  # Northeast  
    120: ([1, 1],   "SE"),  # Southeast
    180: ([1, 0],   "S"),   # South
    240: ([1, -1],  "SW"),  # Southwest
    300: ([-1, -1], "NW"),  # Northwest
}

class Node:
    def __init__(self, y, x, parent, heading, g_cost=0):
        self.y = y
        self.x = x
        self.parent = parent
        self.heading = heading  # Store the actual heading (0, 60, 120, etc.)
        self.g_cost = g_cost
        self.h_cost = 0
        self.f_cost = 0

    def __eq__(self, other):
        return isinstance(other, Node) and self.y == other.y and self.x == other.x

    def __hash__(self):
        return hash((self.y, self.x))

class Pathfinder:
    def __init__(self, mapData, meta):
        self.mapData = mapData
        self.startPos = meta["startPos"]
        self.endPos = meta["finishPos"]
        self.rows = meta["rows"]
        self.cols = meta["cols"]

    def getDirSpeed(self, y, x):
        """
        Get wind direction and speed at logical position (y, x)
        y=1 is bottom row, y=30 is top row
        Array indexing: [0] is top row, [29] is bottom row
        """
        array_row = self.rows - y
        array_col = x - 1
        
        windDir = self.mapData["windDir"][array_row][array_col]
        windSpeed = self.mapData["windSpeed"][array_row][array_col]
        return windDir, windSpeed

    def checkValidMove(self, current_y, current_x, heading):
        """Check if a move with given heading is valid from current position"""
        vector, _ = ALLOWED_MOVES[heading]
        ny = current_y + vector[0]
        nx = current_x + vector[1]
        
        # Check bounds (y from 1 to rows, x from 1 to cols)
        if not (1 <= ny <= self.rows and 1 <= nx <= self.cols):
            return False
        
        # Get wind at the CURRENT cell (not destination!)
        # This matches the MATLAB game logic
        wind_dir, _ = self.getDirSpeed(current_y, current_x)
        
        # Calculate relative angle to wind
        rel_angle = relative_wind_angle(heading, wind_dir)
        
        # Must be at least 30° away from wind-from direction (no-go zone)
        return rel_angle >= 30

    def getPossibleMoves(self, node):
        """Get all valid headings from current node"""
        valid_headings = []
        
        # Get wind at current position for debugging
        wind_dir, wind_speed = self.getDirSpeed(node.y, node.x)
        wind_from = (wind_dir + 180) % 360
        
        for heading in ALLOWED_MOVES.keys():
            if self.checkValidMove(node.y, node.x, heading):
                valid_headings.append(heading)
        
        # Debug: show when we have very few options
        if len(valid_headings) <= 2 and node.y < 25:
            rel_angles = []
            for heading in ALLOWED_MOVES.keys():
                rel = relative_wind_angle(heading, wind_dir)
                status = "✓" if heading in valid_headings else "✗"
                rel_angles.append(f"{ALLOWED_MOVES[heading][1]}:{rel:.0f}°{status}")
            print(f"  Limited moves at ({node.y},{node.x}): wind={wind_dir}° from={wind_from}° -> {', '.join(rel_angles)}")
        
        return valid_headings
    
    def heuristic(self, y, x):
        """Manhattan distance to goal"""
        return abs(self.endPos[0] - y) + abs(self.endPos[1] - x)
    
    def search(self):
        """A* pathfinding algorithm"""
        frontier = []
        explored = set()
        
        # Start node has no heading yet
        start = Node(self.startPos[0], self.startPos[1], None, None, 0)
        start.h_cost = self.heuristic(start.y, start.x)
        start.f_cost = start.g_cost + start.h_cost
        
        frontier.append(start)
        
        iterations = 0
        max_iterations = 100000
        
        print(f"Starting search from {self.startPos} to {self.endPos}")
        start_wind = self.getDirSpeed(self.startPos[0], self.startPos[1])
        end_wind = self.getDirSpeed(self.endPos[0], self.endPos[1])
        print(f"Start wind: dir={start_wind[0]}°, speed={start_wind[1]:.2f}")
        print(f"End wind: dir={end_wind[0]}°, speed={end_wind[1]:.2f}")
        
        while len(frontier) > 0 and iterations < max_iterations:
            iterations += 1
            
            # Get node with lowest f_cost
            frontier.sort(key=lambda n: n.f_cost)
            current = frontier.pop(0)
            
            # Check if we reached the goal
            if current.y == self.endPos[0] and current.x == self.endPos[1]:
                print(f"\n✓ Found route in {iterations} iterations!")
                return self.reconstructPath(current)
            
            explored.add((current.y, current.x))
            
            # Get all valid headings from current position
            valid_headings = self.getPossibleMoves(current)
            
            if iterations % 5000 == 0:
                print(f"Iteration {iterations}: pos=({current.y},{current.x}), "
                      f"moves={len(valid_headings)}, frontier={len(frontier)}, explored={len(explored)}")
            
            for heading in valid_headings:
                vector, _ = ALLOWED_MOVES[heading]
                ny = current.y + vector[0]
                nx = current.x + vector[1]
                
                if (ny, nx) in explored:
                    continue
                
                # Cost is 1 per move
                new_g_cost = current.g_cost + 1
                
                # Check if node already in frontier
                existing_idx = None
                for i, node in enumerate(frontier):
                    if node.y == ny and node.x == nx:
                        existing_idx = i
                        break
                
                if existing_idx is None:
                    # Add new node to frontier
                    new_node = Node(ny, nx, current, heading, new_g_cost)
                    new_node.h_cost = self.heuristic(ny, nx)
                    new_node.f_cost = new_node.g_cost + new_node.h_cost
                    frontier.append(new_node)
                else:
                    # Update existing node if we found a better path
                    node = frontier[existing_idx]
                    if new_g_cost < node.g_cost:
                        node.g_cost = new_g_cost
                        node.f_cost = node.g_cost + node.h_cost
                        node.parent = current
                        node.heading = heading
        
        print(f"\n✗ No route found after {iterations} iterations!")
        print(f"Final frontier size: {len(frontier)}, explored: {len(explored)}")
        return None
    
    def reconstructPath(self, goal_node):
        """Reconstruct path from goal to start"""
        path = []
        current = goal_node
        
        while current.parent is not None:
            path.append(current.heading)
            current = current.parent
        
        path.reverse()
        
        # Convert to compass directions and write to file
        route_lines = []
        for heading in path:
            _, compass_name = ALLOWED_MOVES[heading]
            route_lines.append(compass_name)
        
        route = "\n".join(route_lines)
        
        with open("route.txt", "w") as f:
            f.write(route)
        
        print(f"Route length: {len(path)} moves")
        print(f"Route saved to route.txt")
        
        # Show first few moves
        print("\nFirst 10 moves:")
        for i, heading in enumerate(path[:10]):
            _, name = ALLOWED_MOVES[heading]
            print(f"  {i+1}. {name} ({heading}°)")
        if len(path) > 10:
            print(f"  ... ({len(path) - 10} more moves)")
        
        return route

def validate_route(mapData, meta, route_file="route.txt"):
    """Validate a route by simulating the exact game logic"""
    print("\n" + "="*60)
    print("VALIDATING ROUTE MOVE-BY-MOVE")
    print("="*60)
    
    with open(route_file, 'r') as f:
        moves = [line.strip() for line in f if line.strip()]
    
    # Reverse lookup: compass name to heading
    name_to_heading = {}
    for heading, (vector, name) in ALLOWED_MOVES.items():
        name_to_heading[name] = heading
    
    y, x = meta["startPos"]
    rows, cols = meta["rows"], meta["cols"]
    
    print(f"Start: ({y}, {x})")
    print(f"Goal: {meta['finishPos']}")
    print(f"Total moves in route: {len(moves)}\n")
    
    successful_moves = 0
    
    for i, move_name in enumerate(moves):
        if move_name not in name_to_heading:
            print(f"❌ Move {i+1}: Invalid move name '{move_name}'")
            break
        
        heading = name_to_heading[move_name]
        vector, _ = ALLOWED_MOVES[heading]
        
        # Get wind at CURRENT position (where boat is NOW)
        array_row = rows - y
        array_col = x - 1
        wind_to = mapData["windDir"][array_row][array_col]
        wind_from = (wind_to + 180) % 360
        
        # Check no-go zone
        rel_angle = relative_wind_angle(heading, wind_to)
        
        # Calculate new position
        ny = y + vector[0]
        nx = x + vector[1]
        
        # Check bounds
        if not (1 <= ny <= rows and 1 <= nx <= cols):
            print(f"\n❌ INVALID Move {i+1}: {move_name} ({heading}°)")
            print(f"   Current pos: ({y},{x})")
            print(f"   Would go to: ({ny},{nx}) - OUT OF BOUNDS")
            print(f"   Boat stays at ({y},{x}), remaining moves will fail!")
            break
        
        # Check no-go zone
        if rel_angle < 30:
            print(f"\n❌ INVALID Move {i+1}: {move_name} ({heading}°)")
            print(f"   Current pos: ({y},{x})")
            print(f"   Wind at current cell: to {wind_to}°, from {wind_from}°")
            print(f"   Boat heading: {heading}°")
            print(f"   Relative angle: {rel_angle:.1f}° < 30° (TOO CLOSE TO WIND)")
            print(f"   Boat stays at ({y},{x}), remaining moves will fail!")
            
            # Show what moves WOULD be valid here
            print(f"\n   Valid moves from ({y},{x}):")
            for h in sorted(ALLOWED_MOVES.keys()):
                r = relative_wind_angle(h, wind_to)
                v, n = ALLOWED_MOVES[h]
                ty, tx = y + v[0], x + v[1]
                in_bounds = 1 <= ty <= rows and 1 <= tx <= cols
                status = "✓" if r >= 30 and in_bounds else "✗"
                print(f"      {status} {n:3s} ({h:3d}°): rel_angle={r:5.1f}°, to ({ty},{tx})")
            break
        
        # Valid move!
        successful_moves += 1
        if i < 5 or i >= len(moves) - 5:  # Show first 5 and last 5
            print(f"✓ Move {i+1:2d}: {move_name:3s} ({heading:3d}°) at ({y:2d},{x:2d}) -> ({ny:2d},{nx:2d}) [wind from {wind_from:3.0f}°, rel={rel_angle:4.1f}°]")
        elif i == 5:
            print(f"   ... (moves 6-{len(moves)-5} hidden) ...")
        
        y, x = ny, nx
    
    print(f"\n{'='*60}")
    print(f"Successful moves: {successful_moves}/{len(moves)}")
    print(f"Final position: ({y}, {x})")
    
    if (y, x) == tuple(meta["finishPos"]):
        print("✅ ROUTE VALID - Reached goal!")
        return True
    else:
        print(f"❌ Did not reach goal {meta['finishPos']}")
        print(f"   Distance to goal: {abs(meta['finishPos'][0] - y) + abs(meta['finishPos'][1] - x)} cells")
        return False

def main(): 
    mapData, meta = readMap("map_2_Main")
    pathfinder = Pathfinder(mapData, meta)
    result = pathfinder.search()
    
    if result is None:
        print("\n❌ Failed to find a valid route.")
        print("This might mean:")
        print("  - The goal is unreachable with the wind constraints")
        print("  - The no-go zone (30° from wind-from) blocks all paths")
        print("  - There's still a bug in the coordinate system")
    else:
        # Validate the generated route
        validate_route(mapData, meta)

if __name__ == "__main__":
    main()