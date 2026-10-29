"""Application workflow for persisting and applying settings."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Literal, Protocol

from pydantic import ValidationError

from my_boids.options import BoidOptions, PredatorOptions, write_config

SavePhase = Literal["validation", "persistence", "apply"]


class SettingsRuntime(Protocol):
    """Runtime operations needed to apply saved settings."""

    def update_boid_options(self, opts: BoidOptions) -> None: ...

    def update_predator_options(self, opts: PredatorOptions) -> None: ...


class SettingsSaveError(Exception):
    """Describe the phase and persistence state of a failed settings save."""

    def __init__(
        self,
        phase: SavePhase,
        message: str,
        *,
        field: str | None = None,
        persisted: bool = False,
    ) -> None:
        super().__init__(message)
        self.phase = phase
        self.field = field
        self.persisted = persisted


def save_settings(
    *,
    runtime: SettingsRuntime,
    boid_values: Mapping[str, object],
    predator_values: Mapping[str, object],
    config_path: str | Path,
) -> None:
    """Validate settings, persist them, then apply them to the running game."""
    try:
        validated_boids = BoidOptions.model_validate(boid_values)
        validated_predator = PredatorOptions.model_validate(predator_values)
    except ValidationError as exc:
        first_error = exc.errors()[0]
        location = first_error.get("loc", ())
        field = str(location[0]) if location else None
        message = first_error.get("msg", str(exc))
        if field is not None:
            message = f"{field}: {message}"
        raise SettingsSaveError("validation", message, field=field) from exc

    try:
        write_config(
            str(config_path),
            {
                "boids": {
                    "num_boids": str(validated_boids.num_boids),
                    "size": str(validated_boids.size),
                    "max_speed": str(validated_boids.max_speed),
                    "cohesion_factor": str(validated_boids.cohesion_factor),
                    "separation": str(validated_boids.separation),
                    "avoid_factor": str(validated_boids.avoid_factor),
                    "alignment_factor": str(validated_boids.alignment_factor),
                    "visual_range": str(validated_boids.visual_range),
                    "boid_avoid_mode": validated_boids.boid_avoid_mode,
                },
                "predator": {
                    "predator_attack_mode": validated_predator.predator_attack_mode,
                    "predator_detection_range": str(validated_predator.predator_detection_range),
                    "predator_reaction_strength": str(
                        validated_predator.predator_reaction_strength
                    ),
                },
            },
        )
    except Exception as exc:
        raise SettingsSaveError("persistence", str(exc)) from exc

    try:
        runtime.update_boid_options(validated_boids)
        runtime.update_predator_options(validated_predator)
    except Exception as exc:
        raise SettingsSaveError("apply", str(exc), persisted=True) from exc
