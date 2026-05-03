"""
Boid simulation using PyGame and Sprites

This is a legacy entry point that wraps the actual implementation
in src/my_boids/boids_sim.py for backward compatibility.
"""

from my_boids.boids_sim import main

# Call the main function, start up the game
if __name__ == "__main__":
    main()
