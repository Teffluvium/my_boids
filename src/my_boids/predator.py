
from pathlib import Path

import pygame as pg


class Predator(pg.sprite.Sprite):
    """This class represents the predator."""

    def __init__(
        self,
        pos: pg.Vector2 = pg.Vector2(0, 0),
        vel: pg.Vector2 = pg.Vector2(0, 0),
    ):
        super().__init__()

        # Try to load the predator image, fall back to ellipse if not found
        image_path = Path(__file__).parent / "assets" / "bird_diamond.png"
        if image_path.exists():
            try:
                self.orig_image = pg.image.load(str(image_path)).convert()
                self.orig_image = pg.transform.scale(self.orig_image, (20, 40))
                self.orig_image = pg.transform.rotate(self.orig_image, 90)
                self.orig_image.set_colorkey(pg.Color("white"))
            except pg.error:
                # If image loading fails, use ellipse
                self.orig_image = self._create_ellipse_image()
        else:
            # If image doesn't exist, use ellipse
            self.orig_image = self._create_ellipse_image()

        self.image = self.orig_image
        self.rect = self.image.get_rect()
        self.pos = pos
        self.vel = vel
        self.angle: float = 0.0
        self.prev_pos = self.pos

    def _create_ellipse_image(self) -> pg.Surface:
        """Create a simple ellipse surface for the predator.

        Returns:
            pg.Surface: A surface with an ellipse drawn on it.
        """
        surface = pg.Surface((20, 40))
        surface.fill(pg.Color("black"))
        surface.set_colorkey(pg.Color("black"))
        pg.draw.ellipse(
            surface,
            pg.Color("white"),
            [0, 0, *surface.get_size()],
        )
        return surface

    def update(self):
        """Update the predator location."""
        # Store the old position
        self.prev_pos = self.pos

        # Aim at the mouse
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        new_pos, self.vel = move_to(self.pos, mouse_pos, desired_speed=5)

        if new_pos is not None:
            self.pos = new_pos

            # Find the angle of motion and rotate the image
            self.angle = self.vel.angle_to(pg.Vector2(0, 0)) - 180
            self.image = pg.transform.rotate(self.orig_image, self.angle)

            # Move the image to the correct position
            self.rect = self.image.get_rect(center=self.pos)


def move_to(
    curr_pos: pg.Vector2,
    desired_pos: pg.Vector2,
    desired_speed: float = 10,
    tolerance: float = 10,
) -> tuple[pg.Vector2 | None, pg.Vector2]:
    """Move the object toward the desired position.

    Args:
        curr_pos (pg.Vector2): Current position vector
        desired_pos (pg.Vector2): Desired position vector
        desired_speed (float, optional): Desired speed toward new
            position. Defaults to 5.
        tolerance (float, optional): Minimum distance before calculating
            the new position. Defaults to 10.

    Returns:
        new_pos (pg.Vector2): New position vector. None if the object is
            within the tolerance.
        vel (pg.Vector2): Velocity vector
    """
    new_pos = None
    velocity = pg.Vector2(0, 0)

    # Distance from curr_pos to target_pos
    dist = curr_pos.distance_to(desired_pos)

    if dist > tolerance:
        # Velocity vector in direction of desired_pos
        velocity = (desired_pos - curr_pos).normalize() * desired_speed

        # Only update new position if distance is greater zero
        new_pos = curr_pos + velocity

    return new_pos, velocity  # type: ignore
