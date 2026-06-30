"""
04: ROVER AI PATHFINDER (A* ALGORITHM)
This script loads the hazard heatmap and runs a highly optimized A* search algorithm
to find the shortest and safest path from the landing site into the doubly shadowed crater.
"""
import numpy as np
import networkx as nx
import math

def build_graph_from_hazard_map(hazard_map):
    print("[1/3] Building navigable node graph from hazard map...")
    G = nx.grid_2d_graph(*hazard_map.shape)
    
    # Assign edge weights based on the hazard map (cost of moving into a node)
    for (u, v) in G.edges():
        # Cost is distance + terrain hazard penalty
        # Infinite hazard means edge is impassable
        weight = 1.0 + hazard_map[v[0], v[1]] * 10.0 
        G[u][v]['weight'] = weight
        G[v][u]['weight'] = weight
        
    return G

def heuristic(a, b):
    # Manhattan distance heuristic
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def run_astar(G, start, goal):
    print(f"[2/3] Executing A* Pathfinder from {start} to {goal}...")
    try:
        path = nx.astar_path(G, start, goal, heuristic=heuristic, weight='weight')
        return path
    except nx.NetworkXNoPath:
        print("ERROR: No safe path exists to the target!")
        return None

if __name__ == "__main__":
    print("--- INITIATING AI PATHFINDER ---")
    
    # Import the hazard map generation logic from script 03
    import importlib.util
    import sys
    import os
    spec = importlib.util.spec_from_file_location("hazard", os.path.join(os.path.dirname(__file__), "03_hazard_heatmap.py"))
    hazard_mod = importlib.util.module_from_spec(spec)
    sys.modules["hazard"] = hazard_mod
    spec.loader.exec_module(hazard_mod)
    
    dem = hazard_mod.generate_dem()
    slope = hazard_mod.calculate_slope(dem)
    hazard_map = hazard_mod.create_hazard_map(slope)
    
    # Build graph and run
    G = build_graph_from_hazard_map(hazard_map)
    
    start_pos = (10, 10) # Illuminated landing site
    goal_pos = (70, 70)  # Inside the crater
    
    path = run_astar(G, start_pos, goal_pos)
    if path:
        print(f"[3/3] Path found! Sequence contains {len(path)} waypoints.")
        print(f"Sample Waypoints: {path[:3]} ... {path[-3:]}")
    print("--- PROCESS COMPLETE ---\n")
