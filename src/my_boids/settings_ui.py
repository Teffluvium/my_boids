"""Settings dialog UI built with pygame_gui.

Provides a SettingsDialog that opens over the game window and lets the user
view and edit boid configuration.  Screen settings are displayed read-only
(they require an application restart).  Boid settings take effect immediately
after saving.

Layout
------
The dialog is a floating panel centred on the screen.  Inside it there are
two sections:

* **Screen Settings** – non-editable labels/values.
* **Boid Settings** – a scrollable area with one row per parameter, each row
  containing a label, a slider, and a text-entry that both stay in sync.

Three buttons sit at the bottom: Save, Cancel, Reset to Defaults.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

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
    PREDATOR_BEHAVIOR_MODES,
    BoidOptions,
    ScreenOptions,
    load_config,
)

if TYPE_CHECKING:
    from my_boids.game import Game

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------

_DW = 580  # dialog width
_DH = 640  # dialog height

_PAD = 10  # general padding
_ROW_H = 38  # height of each parameter row
_LBL_W = 185  # label column width
_SLD_W = 215  # slider column width
_TXT_W = 90  # text-entry column width
_SEC_H = 28  # section-header height

# Boid field metadata: (label, step, decimal_places)
_BOID_FIELDS: list[tuple[str, str, float, int]] = [
    ("num_boids", "Num Boids", 1.0, 0),
    ("size", "Size", 1.0, 0),
    ("max_speed", "Max Speed", 1.0, 1),
    ("cohesion_factor", "Cohesion Factor", 0.001, 3),
    ("separation", "Separation", 1.0, 1),
    ("avoid_factor", "Avoid Factor", 0.001, 3),
    ("alignment_factor", "Alignment Factor", 0.001, 3),
    ("visual_range", "Visual Range", 1.0, 0),
    ("predator_detection_range", "Predator Detect Range", 1.0, 1),
    ("predator_reaction_strength", "Predator React Strength", 0.01, 2),
]


def _field_range(field_name: str) -> tuple[float, float]:
    """Return (min, max) for a BoidOptions field from Pydantic metadata."""
    field = BoidOptions.model_fields[field_name]
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


# ---------------------------------------------------------------------------
# SettingsDialog
# ---------------------------------------------------------------------------


class SettingsDialog:
    """A modal settings dialog rendered via pygame_gui.

    Parameters
    ----------
    ui_manager:
        The application-level pygame_gui UIManager.
    config_path:
        Path to config.ini used for persistence on Save.
    game:
        Live Game instance whose boid options are updated on Save.
    """

    def __init__(
        self,
        ui_manager: pygame_gui.UIManager,
        config_path: str,
        game: Game,
    ) -> None:
        self._manager = ui_manager
        self._config_path = config_path
        self._game = game

        self._panel: UIPanel | None = None
        self._scroll: UIScrollingContainer | None = None

        # Boid controls keyed by field name
        self._sliders: dict[str, UIHorizontalSlider] = {}
        self._texts: dict[str, UITextEntryLine] = {}
        self._predator_dd: UIDropDownMenu | None = None

        # Buttons
        self._save_btn: UIButton | None = None
        self._cancel_btn: UIButton | None = None
        self._reset_btn: UIButton | None = None

        # Error label (shown inside dialog when validation fails)
        self._error_lbl: UILabel | None = None

        self._open = False

        # Guard against recursive sync callbacks
        self._syncing = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_open(self) -> bool:
        return self._open

    def open(self, screen_size: tuple[int, int]) -> None:
        """Build the UI and populate it with current game settings."""
        if self._open:
            return
        self._open = True
        self._build_ui(screen_size)
        self._populate(self._game.boid_opts, self._game.screen_opts)

    def close(self) -> None:
        """Destroy all dialog UI elements."""
        if not self._open:
            return
        self._open = False
        self._destroy_ui()

    def handle_event(self, event: pg.event.Event) -> None:
        """Dispatch pygame_gui events that belong to this dialog."""
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

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self, screen_size: tuple[int, int]) -> None:
        x = (screen_size[0] - _DW) // 2
        y = (screen_size[1] - _DH) // 2

        # Main panel (acts as dialog background)
        self._panel = UIPanel(
            relative_rect=pg.Rect(x, y, _DW, _DH),
            manager=self._manager,
            starting_height=2,
        )

        inner_w = _DW - 2 * _PAD
        cy = _PAD  # current y inside panel

        # --- Dialog title ---
        UILabel(
            relative_rect=pg.Rect(_PAD, cy, inner_w, _SEC_H + 4),
            text="Settings",
            manager=self._manager,
            container=self._panel,
            object_id="#settings_title",
        )
        cy += _SEC_H + 8

        # --- Screen section header ---
        UILabel(
            relative_rect=pg.Rect(_PAD, cy, inner_w, _SEC_H),
            text="Screen Settings  (read-only – requires restart)",
            manager=self._manager,
            container=self._panel,
            object_id="#section_header",
        )
        cy += _SEC_H + 4

        cy = self._build_screen_section(cy, inner_w)

        # --- Boid section header ---
        UILabel(
            relative_rect=pg.Rect(_PAD, cy, inner_w, _SEC_H),
            text="Boid Settings",
            manager=self._manager,
            container=self._panel,
            object_id="#section_header",
        )
        cy += _SEC_H + 4

        # Scrollable container for boid controls
        btn_area_h = _ROW_H + 2 * _PAD  # bottom button bar height
        error_area_h = _SEC_H + _PAD  # error label space
        predator_row_h = _ROW_H + _PAD  # predator dropdown row below scroll
        scroll_h = _DH - cy - btn_area_h - error_area_h - predator_row_h - 2 * _PAD
        scroll_inner_h = len(_BOID_FIELDS) * _ROW_H

        self._scroll = UIScrollingContainer(
            relative_rect=pg.Rect(_PAD, cy, inner_w, scroll_h),
            manager=self._manager,
            container=self._panel,
            starting_height=1,
        )
        self._scroll.set_scrollable_area_dimensions((inner_w - 16, scroll_inner_h))
        cy += scroll_h + _PAD

        self._build_boid_controls(inner_w - 16)

        # --- Predator mode dropdown (outside scroll so the expanded list is not clipped) ---
        UILabel(
            relative_rect=pg.Rect(_PAD, cy, _LBL_W, _ROW_H),
            text="Predator Mode",
            manager=self._manager,
            container=self._panel,
        )
        self._predator_dd = UIDropDownMenu(
            options_list=list(PREDATOR_BEHAVIOR_MODES),
            starting_option=self._game.boid_opts.predator_behavior_mode,
            relative_rect=pg.Rect(_PAD + _LBL_W + _PAD, cy, _SLD_W + _PAD + _TXT_W, _ROW_H),
            manager=self._manager,
            container=self._panel,
        )
        cy += _ROW_H + _PAD

        # --- Error label ---
        self._error_lbl = UILabel(
            relative_rect=pg.Rect(_PAD, cy, inner_w, _SEC_H),
            text="",
            manager=self._manager,
            container=self._panel,
            object_id="#error_label",
        )
        cy += _SEC_H + _PAD

        # --- Buttons ---
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
        """Add read-only screen parameter rows. Returns updated y position."""
        screen_opts = self._game.screen_opts
        rows = [
            ("Window Size", f"{screen_opts.winsize[0]} x {screen_opts.winsize[1]}"),
            ("Fullscreen", str(screen_opts.fullscreen)),
            ("Boundary Type", screen_opts.boundary_type.name),
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

    def _build_boid_controls(self, scroll_inner_w: int) -> None:
        """Add slider + text-entry rows inside the scrolling container."""
        row_y = 0

        for field_name, label_text, _step, _decimals in _BOID_FIELDS:
            lo, hi = _field_range(field_name)

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
            self._sliders[field_name] = slider

            text = UITextEntryLine(
                relative_rect=pg.Rect(_LBL_W + _PAD + _SLD_W + _PAD, row_y, _TXT_W, _ROW_H),
                manager=self._manager,
                container=self._scroll,
            )
            self._texts[field_name] = text

            row_y += _ROW_H

        # Predator mode dropdown is now in the panel (not the scroll container)
        # so this method only builds slider rows.

    def _destroy_ui(self) -> None:
        if self._panel is not None:
            self._panel.kill()
            self._panel = None
        self._scroll = None
        self._sliders.clear()
        self._texts.clear()
        self._predator_dd = None
        self._save_btn = None
        self._cancel_btn = None
        self._reset_btn = None
        self._error_lbl = None

    # ------------------------------------------------------------------
    # Value population & sync
    # ------------------------------------------------------------------

    def _populate(self, boid_opts: BoidOptions, _screen_opts: ScreenOptions) -> None:
        """Set all controls to reflect *boid_opts*."""
        self._syncing = True
        try:
            for field_name, _label, _step, decimals in _BOID_FIELDS:
                value = float(getattr(boid_opts, field_name))
                lo, hi = _field_range(field_name)
                clamped = max(lo, min(hi, value))
                self._sliders[field_name].set_current_value(clamped)
                self._texts[field_name].set_text(f"{value:.{decimals}f}")

            if self._predator_dd is not None:
                # pygame_gui UIDropDownMenu does not update its visual state
                # when selected_option is assigned directly, so recreate it.
                old_rect = self._predator_dd.relative_rect.copy()
                self._predator_dd.kill()
                self._predator_dd = UIDropDownMenu(
                    options_list=list(PREDATOR_BEHAVIOR_MODES),
                    starting_option=boid_opts.predator_behavior_mode,
                    relative_rect=old_rect,
                    manager=self._manager,
                    container=self._panel,
                )
        finally:
            self._syncing = False

    def _on_slider_moved(self, slider: UIHorizontalSlider | None) -> None:
        """Sync text entry to match slider value."""
        if self._syncing or slider is None:
            return
        for field_name, _label, _step, decimals in _BOID_FIELDS:
            if self._sliders.get(field_name) is slider:
                value = slider.get_current_value()
                self._syncing = True
                try:
                    self._texts[field_name].set_text(f"{value:.{decimals}f}")
                finally:
                    self._syncing = False
                break

    def _on_text_finished(self, text_entry: UITextEntryLine | None) -> None:
        """Sync slider to match manually entered text, if valid."""
        if self._syncing or text_entry is None:
            return
        for field_name, _label, _step, decimals in _BOID_FIELDS:
            if self._texts.get(field_name) is text_entry:
                raw = text_entry.get_text().strip()
                try:
                    value = float(raw)
                except ValueError:
                    return
                lo, hi = _field_range(field_name)
                clamped = max(lo, min(hi, value))
                self._syncing = True
                try:
                    self._sliders[field_name].set_current_value(clamped)
                    # If clamped, update text to reflect the clamp
                    if clamped != value:
                        text_entry.set_text(f"{clamped:.{decimals}f}")
                finally:
                    self._syncing = False
                break

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _collect_boid_values(self) -> dict:
        """Read current control values into a plain dict for Pydantic."""
        values: dict = {}
        for field_name, _label, _step, _dec in _BOID_FIELDS:
            raw = self._texts[field_name].get_text().strip()
            try:
                values[field_name] = float(raw)
            except ValueError:
                values[field_name] = raw  # let Pydantic report the error

        if self._predator_dd is not None:
            # selected_option is a tuple (display, value) in pygame_gui; extract first element
            raw_dd = self._predator_dd.selected_option
            values["predator_behavior_mode"] = raw_dd[0] if isinstance(raw_dd, tuple) else raw_dd

        return values

    def _handle_save(self) -> None:
        raw_values = self._collect_boid_values()
        try:
            validated = BoidOptions(**raw_values)
        except ValidationError as exc:
            # Surface a concise summary of the first error
            first = exc.errors()[0]
            field = first.get("loc", ("?",))[0]
            msg = first.get("msg", str(exc))
            self._show_error(f"{field}: {msg}")
            return

        self._clear_error()
        self._write_config(validated)
        self._game.update_boid_options(validated)
        self.close()

    def _handle_reset(self) -> None:
        defaults = BoidOptions.get_defaults()
        self._populate(defaults, self._game.screen_opts)
        self._clear_error()

    # ------------------------------------------------------------------
    # Error display
    # ------------------------------------------------------------------

    def _show_error(self, message: str) -> None:
        if self._error_lbl is not None:
            # Truncate long messages to fit the label
            short = message if len(message) <= 80 else message[:77] + "..."
            self._error_lbl.set_text(short)

    def _clear_error(self) -> None:
        if self._error_lbl is not None:
            self._error_lbl.set_text("")

    # ------------------------------------------------------------------
    # Config persistence
    # ------------------------------------------------------------------

    def _write_config(self, opts: BoidOptions) -> None:
        """Persist boid options to config.ini, preserving comments and layout.

        Performs in-place key=value substitution so that inline comments and
        blank lines in config.ini are not stripped by configparser.
        """
        updates = {
            "num_boids": str(opts.num_boids),
            "size": str(opts.size),
            "max_speed": str(opts.max_speed),
            "cohesion_factor": str(opts.cohesion_factor),
            "separation": str(opts.separation),
            "avoid_factor": str(opts.avoid_factor),
            "alignment_factor": str(opts.alignment_factor),
            "visual_range": str(opts.visual_range),
            "predator_behavior_mode": opts.predator_behavior_mode,
            "predator_detection_range": str(opts.predator_detection_range),
            "predator_reaction_strength": str(opts.predator_reaction_strength),
        }

        with open(self._config_path) as fh:
            lines = fh.readlines()

        new_lines = []
        for line in lines:
            match = re.match(r"^(\s*)(\w+)(\s*=\s*)(.*)", line)
            if match:
                key = match.group(2)
                if key in updates:
                    indent = match.group(1)
                    sep = match.group(3)
                    new_lines.append(f"{indent}{key}{sep}{updates[key]}\n")
                    continue
            new_lines.append(line)

        with open(self._config_path, "w") as fh:
            fh.writelines(new_lines)

        # Invalidate the LRU cache so the next from_config() reads fresh values
        load_config.cache_clear()
