"""Settings dialog UI built with pygame_gui."""

from __future__ import annotations

import pygame as pg
import pygame_gui
from pydantic import ValidationError
from pygame_gui.elements import (
    UIButton,
    UIDropDownMenu,
    UIHorizontalSlider,
    UILabel,
    UIPanel,
    UIScrollingContainer,
    UITextEntryLine,
)

from my_boids.options import (
    PREDATOR_ATTACK_MODES,
    PREDATOR_BEHAVIOR_MODES,
    BoidOptions,
    GameProtocol,
    PredatorOptions,
    ScreenOptions,
    write_config,
)

_DW = 580
_DH = 680

_PAD = 10
_ROW_H = 38
_LBL_W = 185
_SLD_W = 215
_TXT_W = 90
_SEC_H = 28

_BOID_FIELDS: list[tuple[str, str, float, int]] = [
    ("num_boids", "Num Boids", 1.0, 0),
    ("size", "Size", 1.0, 0),
    ("max_speed", "Max Speed", 1.0, 1),
    ("cohesion_factor", "Cohesion Factor", 0.001, 3),
    ("separation", "Separation", 1.0, 1),
    ("avoid_factor", "Avoid Factor", 0.001, 3),
    ("alignment_factor", "Alignment Factor", 0.001, 3),
    ("visual_range", "Visual Range", 1.0, 0),
]

_PREDATOR_FIELDS: list[tuple[str, str, float, int]] = [
    ("predator_detection_range", "Detect Range", 1.0, 1),
    ("predator_reaction_strength", "Reaction Strength", 0.01, 2),
]


def _field_range(
    model_cls: type[BoidOptions] | type[PredatorOptions], field_name: str
) -> tuple[float, float]:
    field = model_cls.model_fields[field_name]
    lo, hi = 0.0, 1.0
    for meta in field.metadata:
        if hasattr(meta, "ge"):
            lo = float(meta.ge)
        if hasattr(meta, "gt"):
            lo = float(meta.gt)
        if hasattr(meta, "le"):
            hi = float(meta.le)
        if hasattr(meta, "lt"):
            hi = float(meta.lt)
    return lo, hi


class SettingsDialog:
    """A modal settings dialog rendered via pygame_gui."""

    def __init__(
        self,
        ui_manager: pygame_gui.UIManager,
        config_path: str,
        game: GameProtocol,
    ) -> None:
        self._manager = ui_manager
        self._config_path = config_path
        self._game = game

        self._panel: UIPanel | None = None
        self._scroll: UIScrollingContainer | None = None

        self._boid_sliders: dict[str, UIHorizontalSlider] = {}
        self._boid_texts: dict[str, UITextEntryLine] = {}
        self._predator_sliders: dict[str, UIHorizontalSlider] = {}
        self._predator_texts: dict[str, UITextEntryLine] = {}
        self._predator_dd: UIDropDownMenu | None = None
        self._attack_strategy_dd: UIDropDownMenu | None = None

        self._save_btn: UIButton | None = None
        self._cancel_btn: UIButton | None = None
        self._reset_btn: UIButton | None = None
        self._error_lbl: UILabel | None = None

        self._open = False
        self._syncing = False

    def is_open(self) -> bool:
        return self._open

    def open(self, screen_size: tuple[int, int]) -> None:
        if self._open:
            return
        self._open = True
        self._build_ui(screen_size)
        self._populate(self._game.boid_opts, self._game.predator_opts, self._game.screen_opts)

    def close(self) -> None:
        if not self._open:
            return
        self._open = False
        self._destroy_ui()

    def handle_event(self, event: pg.event.Event) -> None:
        if not self._open:
            return

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element is self._save_btn:
                self._handle_save()
            elif event.ui_element is self._cancel_btn:
                self.close()
            elif event.ui_element is self._reset_btn:
                self._handle_reset()
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and isinstance(
            event.ui_element, UIHorizontalSlider
        ):
            self._on_slider_moved(event.ui_element)
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and isinstance(
            event.ui_element, UITextEntryLine
        ):
            self._on_text_finished(event.ui_element)

    def _build_ui(self, screen_size: tuple[int, int]) -> None:
        x = (screen_size[0] - _DW) // 2
        y = (screen_size[1] - _DH) // 2
        self._panel = UIPanel(
            relative_rect=pg.Rect(x, y, _DW, _DH),
            manager=self._manager,
            starting_height=2,
        )

        inner_w = _DW - 2 * _PAD
        cy = _PAD

        UILabel(
            relative_rect=pg.Rect(_PAD, cy, inner_w, _SEC_H + 4),
            text="Settings",
            manager=self._manager,
            container=self._panel,
            object_id="#settings_title",
        )
        cy += _SEC_H + 8

        UILabel(
            relative_rect=pg.Rect(_PAD, cy, inner_w, _SEC_H),
            text="Screen Settings  (read-only – requires restart)",
            manager=self._manager,
            container=self._panel,
            object_id="#section_header",
        )
        cy += _SEC_H + 4
        cy = self._build_screen_section(cy, inner_w)

        UILabel(
            relative_rect=pg.Rect(_PAD, cy, inner_w, _SEC_H),
            text="Boid Settings",
            manager=self._manager,
            container=self._panel,
            object_id="#section_header",
        )
        cy += _SEC_H + 4

        btn_area_h = _ROW_H + 2 * _PAD
        error_area_h = _SEC_H + _PAD
        dropdown_rows_h = 2 * (_ROW_H + _PAD)
        scroll_h = _DH - cy - btn_area_h - error_area_h - dropdown_rows_h - 2 * _PAD
        scroll_inner_h = (_SEC_H + len(_BOID_FIELDS) * _ROW_H + _PAD) + (
            _SEC_H + len(_PREDATOR_FIELDS) * _ROW_H + _PAD
        )

        self._scroll = UIScrollingContainer(
            relative_rect=pg.Rect(_PAD, cy, inner_w, scroll_h),
            manager=self._manager,
            container=self._panel,
            starting_height=1,
        )
        self._scroll.set_scrollable_area_dimensions((inner_w - 16, scroll_inner_h))
        cy += scroll_h + _PAD

        self._build_numeric_controls()

        UILabel(
            relative_rect=pg.Rect(_PAD, cy, _LBL_W, _ROW_H),
            text="Predator Mode",
            manager=self._manager,
            container=self._panel,
        )
        self._predator_dd = UIDropDownMenu(
            options_list=list(PREDATOR_BEHAVIOR_MODES),
            starting_option=self._game.predator_opts.predator_behavior_mode,
            relative_rect=pg.Rect(_PAD + _LBL_W + _PAD, cy, _SLD_W + _PAD + _TXT_W, _ROW_H),
            manager=self._manager,
            container=self._panel,
        )
        cy += _ROW_H + _PAD

        UILabel(
            relative_rect=pg.Rect(_PAD, cy, _LBL_W, _ROW_H),
            text="Predator Attack",
            manager=self._manager,
            container=self._panel,
        )
        self._attack_strategy_dd = UIDropDownMenu(
            options_list=list(PREDATOR_ATTACK_MODES),
            starting_option=self._game.predator_opts.predator_attack_mode,
            relative_rect=pg.Rect(_PAD + _LBL_W + _PAD, cy, _SLD_W + _PAD + _TXT_W, _ROW_H),
            manager=self._manager,
            container=self._panel,
        )
        cy += _ROW_H + _PAD

        self._error_lbl = UILabel(
            relative_rect=pg.Rect(_PAD, cy, inner_w, _SEC_H),
            text="",
            manager=self._manager,
            container=self._panel,
            object_id="#error_label",
        )
        cy += _SEC_H + _PAD

        btn_w = (inner_w - 2 * _PAD) // 3
        self._save_btn = UIButton(
            relative_rect=pg.Rect(_PAD, cy, btn_w, _ROW_H),
            text="Save",
            manager=self._manager,
            container=self._panel,
        )
        self._reset_btn = UIButton(
            relative_rect=pg.Rect(_PAD + btn_w + _PAD, cy, btn_w, _ROW_H),
            text="Reset to Defaults",
            manager=self._manager,
            container=self._panel,
        )
        self._cancel_btn = UIButton(
            relative_rect=pg.Rect(_PAD + 2 * (btn_w + _PAD), cy, btn_w, _ROW_H),
            text="Cancel",
            manager=self._manager,
            container=self._panel,
        )

    def _build_screen_section(self, cy: int, inner_w: int) -> int:
        rows = [
            (
                "Window Size",
                f"{self._game.screen_opts.winsize[0]} x {self._game.screen_opts.winsize[1]}",
            ),
            ("Fullscreen", str(self._game.screen_opts.fullscreen)),
            ("Boundary Type", self._game.screen_opts.boundary_type.name),
        ]
        for label_text, value_text in rows:
            UILabel(
                relative_rect=pg.Rect(_PAD, cy, _LBL_W, _ROW_H),
                text=label_text,
                manager=self._manager,
                container=self._panel,
            )
            UILabel(
                relative_rect=pg.Rect(_PAD + _LBL_W + _PAD, cy, inner_w - _LBL_W - _PAD, _ROW_H),
                text=value_text,
                manager=self._manager,
                container=self._panel,
                object_id="#readonly_value",
            )
            cy += _ROW_H
        return cy + _PAD

    def _build_numeric_controls(self) -> None:
        row_y = 0
        UILabel(
            relative_rect=pg.Rect(0, row_y, _LBL_W + _SLD_W + _TXT_W + 2 * _PAD, _SEC_H),
            text="Flock Parameters",
            manager=self._manager,
            container=self._scroll,
            object_id="#section_header",
        )
        row_y += _SEC_H

        for field_name, label_text, _step, _decimals in _BOID_FIELDS:
            self._add_numeric_row(
                row_y, field_name, label_text, BoidOptions, self._boid_sliders, self._boid_texts
            )
            row_y += _ROW_H

        row_y += _PAD
        UILabel(
            relative_rect=pg.Rect(0, row_y, _LBL_W + _SLD_W + _TXT_W + 2 * _PAD, _SEC_H),
            text="Predator Parameters",
            manager=self._manager,
            container=self._scroll,
            object_id="#section_header",
        )
        row_y += _SEC_H

        for field_name, label_text, _step, _decimals in _PREDATOR_FIELDS:
            self._add_numeric_row(
                row_y,
                field_name,
                label_text,
                PredatorOptions,
                self._predator_sliders,
                self._predator_texts,
            )
            row_y += _ROW_H

    def _add_numeric_row(
        self,
        row_y: int,
        field_name: str,
        label_text: str,
        model_cls: type[BoidOptions] | type[PredatorOptions],
        sliders: dict[str, UIHorizontalSlider],
        texts: dict[str, UITextEntryLine],
    ) -> None:
        lo, hi = _field_range(model_cls, field_name)
        UILabel(
            relative_rect=pg.Rect(0, row_y, _LBL_W, _ROW_H),
            text=label_text,
            manager=self._manager,
            container=self._scroll,
        )
        slider = UIHorizontalSlider(
            relative_rect=pg.Rect(_LBL_W + _PAD, row_y, _SLD_W, _ROW_H),
            start_value=lo,
            value_range=(lo, hi),
            manager=self._manager,
            container=self._scroll,
        )
        sliders[field_name] = slider
        text = UITextEntryLine(
            relative_rect=pg.Rect(_LBL_W + _PAD + _SLD_W + _PAD, row_y, _TXT_W, _ROW_H),
            manager=self._manager,
            container=self._scroll,
        )
        texts[field_name] = text

    def _destroy_ui(self) -> None:
        if self._panel is not None:
            self._panel.kill()
            self._panel = None
        self._scroll = None
        self._boid_sliders.clear()
        self._boid_texts.clear()
        self._predator_sliders.clear()
        self._predator_texts.clear()
        self._predator_dd = None
        self._attack_strategy_dd = None
        self._save_btn = None
        self._cancel_btn = None
        self._reset_btn = None
        self._error_lbl = None

    def _populate(
        self,
        boid_opts: BoidOptions,
        predator_opts: PredatorOptions,
        _screen_opts: ScreenOptions,
    ) -> None:
        self._syncing = True
        try:
            for field_name, _label, _step, decimals in _BOID_FIELDS:
                value = float(getattr(boid_opts, field_name))
                lo, hi = _field_range(BoidOptions, field_name)
                clamped = max(lo, min(hi, value))
                self._boid_sliders[field_name].set_current_value(clamped)
                self._boid_texts[field_name].set_text(f"{value:.{decimals}f}")

            for field_name, _label, _step, decimals in _PREDATOR_FIELDS:
                value = float(getattr(predator_opts, field_name))
                lo, hi = _field_range(PredatorOptions, field_name)
                clamped = max(lo, min(hi, value))
                self._predator_sliders[field_name].set_current_value(clamped)
                self._predator_texts[field_name].set_text(f"{value:.{decimals}f}")

            if self._predator_dd is not None:
                old_rect = self._predator_dd.relative_rect.copy()
                self._predator_dd.kill()
                self._predator_dd = UIDropDownMenu(
                    options_list=list(PREDATOR_BEHAVIOR_MODES),
                    starting_option=predator_opts.predator_behavior_mode,
                    relative_rect=old_rect,
                    manager=self._manager,
                    container=self._panel,
                )

            if self._attack_strategy_dd is not None:
                old_rect = self._attack_strategy_dd.relative_rect.copy()
                self._attack_strategy_dd.kill()
                self._attack_strategy_dd = UIDropDownMenu(
                    options_list=list(PREDATOR_ATTACK_MODES),
                    starting_option=predator_opts.predator_attack_mode,
                    relative_rect=old_rect,
                    manager=self._manager,
                    container=self._panel,
                )
        finally:
            self._syncing = False

    def _on_slider_moved(self, slider: UIHorizontalSlider | None) -> None:
        if self._syncing or slider is None:
            return
        for field_name, _label, _step, decimals in _BOID_FIELDS:
            if self._boid_sliders.get(field_name) is slider:
                self._syncing = True
                try:
                    self._boid_texts[field_name].set_text(
                        f"{slider.get_current_value():.{decimals}f}"
                    )
                finally:
                    self._syncing = False
                return
        for field_name, _label, _step, decimals in _PREDATOR_FIELDS:
            if self._predator_sliders.get(field_name) is slider:
                self._syncing = True
                try:
                    self._predator_texts[field_name].set_text(
                        f"{slider.get_current_value():.{decimals}f}"
                    )
                finally:
                    self._syncing = False
                return

    def _on_text_finished(self, text_entry: UITextEntryLine | None) -> None:
        if self._syncing or text_entry is None:
            return
        for field_name, _label, _step, decimals in _BOID_FIELDS:
            if self._boid_texts.get(field_name) is text_entry:
                self._sync_text_to_slider(
                    text_entry, field_name, decimals, BoidOptions, self._boid_sliders
                )
                return
        for field_name, _label, _step, decimals in _PREDATOR_FIELDS:
            if self._predator_texts.get(field_name) is text_entry:
                self._sync_text_to_slider(
                    text_entry,
                    field_name,
                    decimals,
                    PredatorOptions,
                    self._predator_sliders,
                )
                return

    def _sync_text_to_slider(
        self,
        text_entry: UITextEntryLine,
        field_name: str,
        decimals: int,
        model_cls: type[BoidOptions] | type[PredatorOptions],
        sliders: dict[str, UIHorizontalSlider],
    ) -> None:
        raw = text_entry.get_text().strip()
        try:
            value = float(raw)
        except ValueError:
            return
        lo, hi = _field_range(model_cls, field_name)
        clamped = max(lo, min(hi, value))
        self._syncing = True
        try:
            sliders[field_name].set_current_value(clamped)
            if clamped != value:
                text_entry.set_text(f"{clamped:.{decimals}f}")
        finally:
            self._syncing = False

    def _collect_boid_values(self) -> dict[str, object]:
        values: dict[str, object] = {}
        for field_name, _label, _step, _dec in _BOID_FIELDS:
            raw = self._boid_texts[field_name].get_text().strip()
            try:
                values[field_name] = float(raw)
            except ValueError:
                values[field_name] = raw
        return values

    def _collect_predator_values(self) -> dict[str, object]:
        values: dict[str, object] = {}
        for field_name, _label, _step, _dec in _PREDATOR_FIELDS:
            raw = self._predator_texts[field_name].get_text().strip()
            try:
                values[field_name] = float(raw)
            except ValueError:
                values[field_name] = raw

        if self._predator_dd is not None:
            raw_dd = self._predator_dd.selected_option
            values["predator_behavior_mode"] = raw_dd[0] if isinstance(raw_dd, tuple) else raw_dd
        if self._attack_strategy_dd is not None:
            raw_dd = self._attack_strategy_dd.selected_option
            values["predator_attack_mode"] = raw_dd[0] if isinstance(raw_dd, tuple) else raw_dd
        return values

    def _handle_save(self) -> None:
        raw_boid_values = self._collect_boid_values()
        raw_predator_values = self._collect_predator_values()
        try:
            validated_boids = BoidOptions.model_validate(raw_boid_values)
            validated_predator = PredatorOptions.model_validate(raw_predator_values)
        except ValidationError as exc:
            first = exc.errors()[0]
            field = first.get("loc", ("?",))[0]
            msg = first.get("msg", str(exc))
            self._show_error(f"{field}: {msg}")
            return

        self._clear_error()
        write_config(
            self._config_path,
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
                },
                "predator": {
                    "predator_behavior_mode": validated_predator.predator_behavior_mode,
                    "predator_attack_mode": validated_predator.predator_attack_mode,
                    "predator_detection_range": str(validated_predator.predator_detection_range),
                    "predator_reaction_strength": str(
                        validated_predator.predator_reaction_strength
                    ),
                },
            },
        )
        self._game.update_boid_options(validated_boids)
        self._game.update_predator_options(validated_predator)
        self.close()

    def _handle_reset(self) -> None:
        self._populate(
            BoidOptions.get_defaults(),
            PredatorOptions.get_defaults(),
            self._game.screen_opts,
        )
        self._clear_error()

    def _show_error(self, message: str) -> None:
        if self._error_lbl is not None:
            short = message if len(message) <= 80 else message[:77] + "..."
            self._error_lbl.set_text(short)

    def _clear_error(self) -> None:
        if self._error_lbl is not None:
            self._error_lbl.set_text("")
