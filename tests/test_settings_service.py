"""Tests for the settings persistence and runtime application workflow."""

from pathlib import Path

import pytest

from my_boids.options import BoidOptions, PredatorOptions, load_config, write_config
from my_boids.settings_service import SettingsSaveError, save_settings

BOID_VALUES: dict[str, object] = {
    "num_boids": 3,
    "size": 8,
    "max_speed": 15.0,
    "boid_avoid_mode": "attract",
}
PREDATOR_VALUES: dict[str, object] = {
    "predator_attack_mode": "nearest",
    "predator_detection_range": 250.0,
    "predator_reaction_strength": 0.8,
}


class FakeRuntime:
    def __init__(self, fail_on: str | None = None) -> None:
        self.fail_on = fail_on
        self.calls: list[str] = []
        self.boid_options: BoidOptions | None = None
        self.predator_options: PredatorOptions | None = None

    def update_boid_options(self, opts: BoidOptions) -> None:
        self.calls.append("boids")
        self.boid_options = opts
        if self.fail_on == "boids":
            raise RuntimeError("boid update failed")

    def update_predator_options(self, opts: PredatorOptions) -> None:
        self.calls.append("predator")
        self.predator_options = opts
        if self.fail_on == "predator":
            raise RuntimeError("predator update failed")


def _write_config(path: Path) -> None:
    path.write_text(
        """# Keep this comment.
[screen]
winsize = [800, 600]

[boids]
# Preserve this setting comment.
num_boids = 53
size = 10
max_speed = 20.0
cohesion_factor = 0.01
separation = 20.0
avoid_factor = 0.05
alignment_factor = 0.05
visual_range = 40
boid_avoid_mode = avoid

[predator]
predator_attack_mode = center
predator_detection_range = 400.0
predator_reaction_strength = 0.5

[extra]
untouched = yes
"""
    )


def test_save_settings_persists_and_applies_values(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    _write_config(config_path)
    runtime = FakeRuntime()

    assert load_config(str(config_path))["boids"]["num_boids"] == "53"

    save_settings(
        runtime=runtime,
        boid_values=BOID_VALUES,
        predator_values=PREDATOR_VALUES,
        config_path=config_path,
    )

    assert runtime.calls == ["boids", "predator"]
    assert runtime.boid_options is not None
    assert runtime.boid_options.num_boids == 3
    assert runtime.boid_options.boid_avoid_mode == "attract"
    assert runtime.predator_options is not None
    assert runtime.predator_options.predator_attack_mode == "nearest"
    assert load_config(str(config_path))["boids"]["num_boids"] == "3"

    text = config_path.read_text()
    assert "# Keep this comment." in text
    assert "# Preserve this setting comment.\nnum_boids = 3" in text
    assert "[extra]\nuntouched = yes" in text


@pytest.mark.parametrize(
    ("boid_values", "predator_values", "field"),
    [
        ({**BOID_VALUES, "num_boids": 0}, PREDATOR_VALUES, "num_boids"),
        (
            BOID_VALUES,
            {**PREDATOR_VALUES, "predator_reaction_strength": 0},
            "predator_reaction_strength",
        ),
    ],
)
def test_save_settings_rejects_invalid_values_without_side_effects(
    tmp_path: Path,
    boid_values: dict[str, object],
    predator_values: dict[str, object],
    field: str,
) -> None:
    config_path = tmp_path / "config.ini"
    _write_config(config_path)
    original_config = config_path.read_text()
    runtime = FakeRuntime()

    with pytest.raises(SettingsSaveError) as error:
        save_settings(
            runtime=runtime,
            boid_values=boid_values,
            predator_values=predator_values,
            config_path=config_path,
        )

    assert error.value.phase == "validation"
    assert error.value.field == field
    assert not error.value.persisted
    assert runtime.calls == []
    assert config_path.read_text() == original_config


def test_save_settings_reports_persistence_failure_without_applying(tmp_path: Path) -> None:
    config_path = tmp_path / "missing" / "config.ini"
    runtime = FakeRuntime()

    with pytest.raises(SettingsSaveError) as error:
        save_settings(
            runtime=runtime,
            boid_values=BOID_VALUES,
            predator_values=PREDATOR_VALUES,
            config_path=config_path,
        )

    assert error.value.phase == "persistence"
    assert not error.value.persisted
    assert isinstance(error.value.__cause__, FileNotFoundError)
    assert runtime.calls == []


def test_save_settings_reports_persisted_state_when_apply_fails(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    _write_config(config_path)
    runtime = FakeRuntime(fail_on="predator")

    with pytest.raises(SettingsSaveError) as error:
        save_settings(
            runtime=runtime,
            boid_values=BOID_VALUES,
            predator_values=PREDATOR_VALUES,
            config_path=config_path,
        )

    assert error.value.phase == "apply"
    assert error.value.persisted
    assert isinstance(error.value.__cause__, RuntimeError)
    assert runtime.calls == ["boids", "predator"]
    assert "num_boids = 3" in config_path.read_text()


@pytest.mark.parametrize("has_predator_section", [False, True])
@pytest.mark.parametrize("trailing_newline", [False, True])
def test_write_config_inserts_motion_keys_in_their_own_sections(
    tmp_path: Path, has_predator_section: bool, trailing_newline: bool
) -> None:
    config_path = tmp_path / "motion.ini"
    original = (
        "# Keep this comment.\n[boids]\nmax_speed = 8.0  # Flock speed\n\n"
        + ("[predator]\npredator_attack_mode = nearest\n\n" if has_predator_section else "")
        + "[extra]\nuntouched = yes"
        + ("\n" if trailing_newline else "")
    )
    config_path.write_text(original)
    assert load_config(str(config_path))["boids"]["max_speed"] == "8.0  # Flock speed"

    updates = {
        "boids": {"max_acceleration": "0.31", "max_deceleration": "0.14"},
        "predator": {"max_speed": "6.75", "max_acceleration": "0.62", "max_deceleration": "0.23"},
    }
    write_config(str(config_path), updates)

    config = load_config(str(config_path))
    for section, values in updates.items():
        for field, value in values.items():
            assert config[section][field] == value
    assert dict(config["extra"]) == {"untouched": "yes"}
    text = config_path.read_text()
    assert "# Keep this comment.\n[boids]\nmax_speed = 8.0  # Flock speed" in text
    write_config(str(config_path), updates)
    assert config_path.read_text() == text


def test_save_settings_round_trips_independent_motion_values(tmp_path: Path) -> None:
    config_path = tmp_path / "config.ini"
    _write_config(config_path)
    runtime = FakeRuntime()
    boid_values = {**BOID_VALUES, "max_acceleration": 0.31, "max_deceleration": 0.14}
    predator_values = {
        **PREDATOR_VALUES,
        "max_speed": 6.75,
        "max_acceleration": 0.62,
        "max_deceleration": 0.23,
    }
    assert BoidOptions.from_config(str(config_path)).max_acceleration == 0.5

    save_settings(
        runtime=runtime,
        boid_values=boid_values,
        predator_values=predator_values,
        config_path=config_path,
    )

    assert runtime.boid_options is not None
    assert runtime.predator_options is not None
    assert runtime.boid_options == BoidOptions.model_validate(boid_values)
    assert runtime.predator_options == PredatorOptions.model_validate(predator_values)
    assert BoidOptions.from_config(str(config_path)) == runtime.boid_options
    assert PredatorOptions.from_config(str(config_path)) == runtime.predator_options
    assert runtime.calls == ["boids", "predator"]
    assert dict(load_config(str(config_path))["extra"]) == {"untouched": "yes"}

    text = config_path.read_text()
    assert "# Keep this comment." in text
    assert "# Preserve this setting comment." in text
    save_settings(
        runtime=runtime,
        boid_values=boid_values,
        predator_values=predator_values,
        config_path=config_path,
    )
    assert config_path.read_text() == text


@pytest.mark.parametrize(
    "section, field",
    [
        ("boids", "max_acceleration"),
        ("boids", "max_deceleration"),
        ("predator", "max_speed"),
        ("predator", "max_acceleration"),
        ("predator", "max_deceleration"),
    ],
)
@pytest.mark.parametrize("invalid", [0, -1, 50.1, float("nan"), float("inf"), -float("inf")])
def test_invalid_motion_save_has_no_side_effects(
    tmp_path: Path, section: str, field: str, invalid: float
) -> None:
    config_path = tmp_path / "config.ini"
    _write_config(config_path)
    original = config_path.read_text()
    runtime = FakeRuntime()
    values = {"boids": BOID_VALUES.copy(), "predator": PREDATOR_VALUES.copy()}
    values[section][field] = invalid

    with pytest.raises(SettingsSaveError) as error:
        save_settings(
            runtime=runtime,
            boid_values=values["boids"],
            predator_values=values["predator"],
            config_path=config_path,
        )

    assert error.value.phase == "validation"
    assert error.value.field == field
    assert not error.value.persisted
    assert runtime.calls == []
    assert runtime.boid_options is None
    assert runtime.predator_options is None
    assert config_path.read_text() == original
