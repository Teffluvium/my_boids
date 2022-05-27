"""
Create a boid and define its movement rules
"""
import pygame as pg

# Boid Constants
SIZE = 10
MAX_SPEED = 3


class Boid(pg.sprite.Sprite):
    """A single Boid"""

    def __init__(
        self,
        pos: pg.Vector2 = pg.Vector2(0, 0),
        vel: pg.Vector2 = pg.Vector2(0, 0),
        color: pg.Color = pg.Color(255, 255, 255),
        size: int = 10,
        width: int = 10,
        height: int = 10,
    ):
        """Constructor"""
        # Call the Sprite initializer
        super().__init__()

        ## Validate parameters
        # Ensure that position and velocity are Vector2 objects
        self.pos = pos if isinstance(pos, pg.Vector2) else pg.Vetor2(pos)
        self.vel = vel if isinstance(vel, pg.Vector2) else pg.Vetor2(vel)

        # Ensure color is a tuple and has 3 or 4 elements
        self.color = color if isinstance(color, pg.Color) else pg.Color(color)

        # Check size is a positive
        if size >= 1:
            self.size = size
        else:
            raise ValueError("Size cannot be negative")

        # Create a surface for the boid
        self.image = pg.Surface([width, height])

        # Fill the surface with the the background color and set it to be transparent
        self.image.fill(pg.Color("black"))
        self.image.set_colorkey(pg.Color("black"))

        # Draw the boid onto the surface
        pg.draw.ellipse(self.image, color, [0, 0, width, height])

        # Get a rectangle object that represents the size of the image
        self.rect = self.image.get_rect()

        self.rect.center = self.pos

    def update(self):
        """Called each frame. Updates the position of the boid."""
        # # Move the boid based on its velocity
        self.pos += self.vel

        # Update the rectangle position
        self.rect.center = self.pos

    def speed_limit(self, max_speed: float = MAX_SPEED):
        """Limit the speed of the boid"""
        speed = self.vel.magnitude()
        # Apply a speed limit
        if speed > max_speed:
            self.vel.scale_to_length(max_speed)


if __name__ == "__main__":
    # The main
    print("Boids")
