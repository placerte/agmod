"""Everforest themes for Textual TUI apps.

Official palette: https://github.com/sainnhe/everforest/blob/master/palette.md

All 6 variants are provided:
  - everforest-dark-hard, everforest-dark-medium, everforest-dark-soft
  - everforest-light-hard, everforest-light-medium, everforest-light-soft

Usage — copy this file into any Textual project and add to your App::

    from themes import EVERFOREST_THEMES, register_everforest_themes

    class MyApp(App):
        def on_mount(self) -> None:
            register_everforest_themes(self)
            self.theme = "everforest-dark-hard"
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.theme import Theme

if TYPE_CHECKING:
    from textual.app import App


# ---------------------------------------------------------------------------
# Dark palette — foreground accents (shared across hard/medium/soft)
# ---------------------------------------------------------------------------

_DARK_FG = "#D3C6AA"
_DARK_RED = "#E67E80"
_DARK_ORANGE = "#E69875"
_DARK_YELLOW = "#DBBC7F"
_DARK_GREEN = "#A7C080"
_DARK_AQUA = "#83C092"
_DARK_BLUE = "#7FBBB3"
_DARK_PURPLE = "#D699B6"
_DARK_GREY0 = "#7A8478"
_DARK_GREY1 = "#859289"
_DARK_GREY2 = "#9DA9A0"

# ---------------------------------------------------------------------------
# Dark Hard backgrounds  (bg_dim … bg5 + tinted bg_*)
# ---------------------------------------------------------------------------

_DH_BG_DIM = "#1E2326"
_DH_BG0 = "#272E33"
_DH_BG1 = "#2E383C"
_DH_BG2 = "#374145"
_DH_BG3 = "#414B50"
_DH_BG4 = "#495156"
_DH_BG5 = "#4F5B58"
_DH_BG_RED = "#493B40"
_DH_BG_YELLOW = "#45443C"
_DH_BG_GREEN = "#3C4841"
_DH_BG_BLUE = "#384B55"
_DH_BG_PURPLE = "#463F48"
_DH_BG_VISUAL = "#4C3743"

# ---------------------------------------------------------------------------
# Dark Medium backgrounds
# ---------------------------------------------------------------------------

_DM_BG_DIM = "#232A2E"
_DM_BG0 = "#2D353B"
_DM_BG1 = "#343F44"
_DM_BG2 = "#3D484D"
_DM_BG3 = "#475258"
_DM_BG4 = "#4F585E"
_DM_BG5 = "#56635F"
_DM_BG_RED = "#514045"
_DM_BG_YELLOW = "#4D4C43"
_DM_BG_GREEN = "#425047"
_DM_BG_BLUE = "#3A515D"
_DM_BG_PURPLE = "#4A444E"
_DM_BG_VISUAL = "#543A48"

# ---------------------------------------------------------------------------
# Dark Soft backgrounds
# ---------------------------------------------------------------------------

_DS_BG_DIM = "#293136"
_DS_BG0 = "#333C43"
_DS_BG1 = "#3A464C"
_DS_BG2 = "#434F55"
_DS_BG3 = "#4D5960"
_DS_BG4 = "#555F66"
_DS_BG5 = "#5D6B66"
_DS_BG_RED = "#59464C"
_DS_BG_YELLOW = "#55544A"
_DS_BG_GREEN = "#48584E"
_DS_BG_BLUE = "#3F5865"
_DS_BG_PURPLE = "#4E4953"
_DS_BG_VISUAL = "#5C3F4F"

# ---------------------------------------------------------------------------
# Light palette — foreground accents (shared across hard/medium/soft)
# ---------------------------------------------------------------------------

_LIGHT_FG = "#5C6A72"
_LIGHT_RED = "#F85552"
_LIGHT_ORANGE = "#F57D26"
_LIGHT_YELLOW = "#DFA000"
_LIGHT_GREEN = "#8DA101"
_LIGHT_AQUA = "#35A77C"
_LIGHT_BLUE = "#3A94C5"
_LIGHT_PURPLE = "#DF69BA"
_LIGHT_GREY0 = "#A6B0A0"
_LIGHT_GREY1 = "#939F91"
_LIGHT_GREY2 = "#829181"

# ---------------------------------------------------------------------------
# Light Hard backgrounds
# ---------------------------------------------------------------------------

_LH_BG_DIM = "#F2EFDF"
_LH_BG0 = "#FFFBEF"
_LH_BG1 = "#F8F5E4"
_LH_BG2 = "#F2EFDF"
_LH_BG3 = "#EDEADA"
_LH_BG4 = "#E8E5D5"
_LH_BG5 = "#BEC5B2"
_LH_BG_RED = "#FFE7DE"
_LH_BG_YELLOW = "#FEF2D5"
_LH_BG_GREEN = "#F3F5D9"
_LH_BG_BLUE = "#ECF5ED"
_LH_BG_PURPLE = "#FCECED"
_LH_BG_VISUAL = "#F0F2D4"

# ---------------------------------------------------------------------------
# Light Medium backgrounds
# ---------------------------------------------------------------------------

_LM_BG_DIM = "#EFEBD4"
_LM_BG0 = "#FDF6E3"
_LM_BG1 = "#F4F0D9"
_LM_BG2 = "#EFEBD4"
_LM_BG3 = "#E6E2CC"
_LM_BG4 = "#E0DCC7"
_LM_BG5 = "#BDC3AF"
_LM_BG_RED = "#FDE3DA"
_LM_BG_YELLOW = "#FAEDCD"
_LM_BG_GREEN = "#F0F1D2"
_LM_BG_BLUE = "#E9F0E9"
_LM_BG_PURPLE = "#FAE8E2"
_LM_BG_VISUAL = "#EAEDC8"

# ---------------------------------------------------------------------------
# Light Soft backgrounds
# ---------------------------------------------------------------------------

_LS_BG_DIM = "#E5DFC5"
_LS_BG0 = "#F3EAD3"
_LS_BG1 = "#EAE4CA"
_LS_BG2 = "#E5DFC5"
_LS_BG3 = "#DDD8BE"
_LS_BG4 = "#D8D3BA"
_LS_BG5 = "#B9C0AB"
_LS_BG_RED = "#FADBD0"
_LS_BG_YELLOW = "#F1E4C5"
_LS_BG_GREEN = "#E5E6C5"
_LS_BG_BLUE = "#E1E7DD"
_LS_BG_PURPLE = "#F1DDD4"
_LS_BG_VISUAL = "#E1E4BD"


# ---------------------------------------------------------------------------
# Shared variable-override builder
# ---------------------------------------------------------------------------


def _dark_variables(
    bg_dim: str,
    bg0: str,
    bg1: str,
    bg2: str,
    bg3: str,
    bg4: str,
    bg5: str,
    bg_red: str,
    bg_yellow: str,
    bg_green: str,
    bg_blue: str,
    bg_purple: str,
    bg_visual: str,
) -> dict[str, str]:
    """Build the ``variables`` override dict for a dark Everforest variant.

    Maps official palette backgrounds into Textual shade variables so that
    darken/lighten steps use the hand-tuned Everforest values instead of
    auto-generated Lab luminosity shifts.
    """
    return {
        # -- background shades (bg_dim → bg0 → bg1 → bg2 → bg3 → bg4 → bg5)
        "background-darken-3": bg_dim,
        "background-darken-2": bg_dim,
        "background-darken-1": bg_dim,
        # "background" is the base, set via Theme.background
        "background-lighten-1": bg1,
        "background-lighten-2": bg2,
        "background-lighten-3": bg3,
        # -- surface shades (surface = bg1)
        "surface-darken-3": bg_dim,
        "surface-darken-2": bg0,
        "surface-darken-1": bg0,
        # "surface" is the base (bg1), set via Theme.surface
        "surface-lighten-1": bg2,
        "surface-lighten-2": bg3,
        "surface-lighten-3": bg4,
        # -- panel shades (panel = bg2)
        "panel-darken-3": bg0,
        "panel-darken-2": bg1,
        "panel-darken-1": bg1,
        # "panel" is the base (bg2), set via Theme.panel
        "panel-lighten-1": bg3,
        "panel-lighten-2": bg4,
        "panel-lighten-3": bg5,
        # -- muted accent variants using Everforest tinted backgrounds
        "error-muted": bg_red,
        "warning-muted": bg_yellow,
        "success-muted": bg_green,
        "primary-muted": bg_green,
        "secondary-muted": bg_blue,
        "accent-muted": bg_purple,
        # -- cursor / selection using Everforest visual selection colour
        "block-cursor-background": _DARK_GREEN,
        "block-cursor-foreground": bg0,
        "block-cursor-text-style": "none",
        "block-cursor-blurred-background": bg3,
        "block-cursor-blurred-foreground": _DARK_FG,
        "block-cursor-blurred-text-style": "none",
        "block-hover-background": bg2,
        "input-selection-background": f"{_DARK_BLUE} 35%",
        # -- footer
        "footer-foreground": _DARK_FG,
        "footer-background": bg1,
        "footer-key-foreground": _DARK_GREEN,
        "footer-key-background": bg2,
        "footer-description-foreground": _DARK_FG,
        "footer-description-background": bg1,
        "footer-item-background": bg1,
        # -- borders
        "border": _DARK_GREY0,
        "border-blurred": bg3,
        # -- scrollbar
        "scrollbar": bg4,
        "scrollbar-hover": bg5,
        "scrollbar-active": _DARK_GREY0,
        "scrollbar-background": bg1,
        "scrollbar-background-hover": bg1,
        "scrollbar-background-active": bg1,
        "scrollbar-corner-color": bg1,
        # -- button
        "button-foreground": _DARK_FG,
        "button-color-foreground": bg0,
        "button-focus-text-style": "reverse",
    }


def _light_variables(
    bg_dim: str,
    bg0: str,
    bg1: str,
    bg2: str,
    bg3: str,
    bg4: str,
    bg5: str,
    bg_red: str,
    bg_yellow: str,
    bg_green: str,
    bg_blue: str,
    bg_purple: str,
    bg_visual: str,
) -> dict[str, str]:
    """Build the ``variables`` override dict for a light Everforest variant."""
    return {
        # -- background shades
        "background-darken-1": bg1,
        "background-darken-2": bg2,
        "background-darken-3": bg3,
        # "background" base = bg0
        "background-lighten-1": bg0,
        "background-lighten-2": bg0,
        "background-lighten-3": bg0,
        # -- surface shades (surface = bg1)
        "surface-darken-1": bg2,
        "surface-darken-2": bg3,
        "surface-darken-3": bg4,
        # "surface" base = bg1
        "surface-lighten-1": bg0,
        "surface-lighten-2": bg0,
        "surface-lighten-3": bg_dim,
        # -- panel shades (panel = bg2)
        "panel-darken-1": bg3,
        "panel-darken-2": bg4,
        "panel-darken-3": bg5,
        # "panel" base = bg2
        "panel-lighten-1": bg1,
        "panel-lighten-2": bg0,
        "panel-lighten-3": bg0,
        # -- muted accent variants using Everforest tinted backgrounds
        "error-muted": bg_red,
        "warning-muted": bg_yellow,
        "success-muted": bg_green,
        "primary-muted": bg_green,
        "secondary-muted": bg_blue,
        "accent-muted": bg_purple,
        # -- cursor / selection
        "block-cursor-background": _LIGHT_GREEN,
        "block-cursor-foreground": bg0,
        "block-cursor-text-style": "none",
        "block-cursor-blurred-background": bg3,
        "block-cursor-blurred-foreground": _LIGHT_FG,
        "block-cursor-blurred-text-style": "none",
        "block-hover-background": bg2,
        "input-selection-background": f"{_LIGHT_BLUE} 35%",
        # -- footer
        "footer-foreground": _LIGHT_FG,
        "footer-background": bg1,
        "footer-key-foreground": _LIGHT_GREEN,
        "footer-key-background": bg2,
        "footer-description-foreground": _LIGHT_FG,
        "footer-description-background": bg1,
        "footer-item-background": bg1,
        # -- borders
        "border": _LIGHT_GREY1,
        "border-blurred": bg3,
        # -- scrollbar
        "scrollbar": bg4,
        "scrollbar-hover": bg5,
        "scrollbar-active": _LIGHT_GREY1,
        "scrollbar-background": bg1,
        "scrollbar-background-hover": bg1,
        "scrollbar-background-active": bg1,
        "scrollbar-corner-color": bg1,
        # -- button
        "button-foreground": _LIGHT_FG,
        "button-color-foreground": bg0,
        "button-focus-text-style": "reverse",
    }


# ---------------------------------------------------------------------------
# Theme definitions
# ---------------------------------------------------------------------------

EVERFOREST_DARK_HARD = Theme(
    name="everforest-dark-hard",
    primary=_DARK_GREEN,
    secondary=_DARK_BLUE,
    accent=_DARK_PURPLE,
    warning=_DARK_YELLOW,
    error=_DARK_RED,
    success=_DARK_AQUA,
    foreground=_DARK_FG,
    background=_DH_BG0,
    surface=_DH_BG1,
    panel=_DH_BG2,
    dark=True,
    luminosity_spread=0.15,
    text_alpha=0.95,
    variables=_dark_variables(
        bg_dim=_DH_BG_DIM,
        bg0=_DH_BG0,
        bg1=_DH_BG1,
        bg2=_DH_BG2,
        bg3=_DH_BG3,
        bg4=_DH_BG4,
        bg5=_DH_BG5,
        bg_red=_DH_BG_RED,
        bg_yellow=_DH_BG_YELLOW,
        bg_green=_DH_BG_GREEN,
        bg_blue=_DH_BG_BLUE,
        bg_purple=_DH_BG_PURPLE,
        bg_visual=_DH_BG_VISUAL,
    ),
)

EVERFOREST_DARK_MEDIUM = Theme(
    name="everforest-dark-medium",
    primary=_DARK_GREEN,
    secondary=_DARK_BLUE,
    accent=_DARK_PURPLE,
    warning=_DARK_YELLOW,
    error=_DARK_RED,
    success=_DARK_AQUA,
    foreground=_DARK_FG,
    background=_DM_BG0,
    surface=_DM_BG1,
    panel=_DM_BG2,
    dark=True,
    luminosity_spread=0.15,
    text_alpha=0.95,
    variables=_dark_variables(
        bg_dim=_DM_BG_DIM,
        bg0=_DM_BG0,
        bg1=_DM_BG1,
        bg2=_DM_BG2,
        bg3=_DM_BG3,
        bg4=_DM_BG4,
        bg5=_DM_BG5,
        bg_red=_DM_BG_RED,
        bg_yellow=_DM_BG_YELLOW,
        bg_green=_DM_BG_GREEN,
        bg_blue=_DM_BG_BLUE,
        bg_purple=_DM_BG_PURPLE,
        bg_visual=_DM_BG_VISUAL,
    ),
)

EVERFOREST_DARK_SOFT = Theme(
    name="everforest-dark-soft",
    primary=_DARK_GREEN,
    secondary=_DARK_BLUE,
    accent=_DARK_PURPLE,
    warning=_DARK_YELLOW,
    error=_DARK_RED,
    success=_DARK_AQUA,
    foreground=_DARK_FG,
    background=_DS_BG0,
    surface=_DS_BG1,
    panel=_DS_BG2,
    dark=True,
    luminosity_spread=0.15,
    text_alpha=0.95,
    variables=_dark_variables(
        bg_dim=_DS_BG_DIM,
        bg0=_DS_BG0,
        bg1=_DS_BG1,
        bg2=_DS_BG2,
        bg3=_DS_BG3,
        bg4=_DS_BG4,
        bg5=_DS_BG5,
        bg_red=_DS_BG_RED,
        bg_yellow=_DS_BG_YELLOW,
        bg_green=_DS_BG_GREEN,
        bg_blue=_DS_BG_BLUE,
        bg_purple=_DS_BG_PURPLE,
        bg_visual=_DS_BG_VISUAL,
    ),
)

EVERFOREST_LIGHT_HARD = Theme(
    name="everforest-light-hard",
    primary=_LIGHT_GREEN,
    secondary=_LIGHT_BLUE,
    accent=_LIGHT_PURPLE,
    warning=_LIGHT_YELLOW,
    error=_LIGHT_RED,
    success=_LIGHT_AQUA,
    foreground=_LIGHT_FG,
    background=_LH_BG0,
    surface=_LH_BG1,
    panel=_LH_BG2,
    dark=False,
    luminosity_spread=0.15,
    text_alpha=0.95,
    variables=_light_variables(
        bg_dim=_LH_BG_DIM,
        bg0=_LH_BG0,
        bg1=_LH_BG1,
        bg2=_LH_BG2,
        bg3=_LH_BG3,
        bg4=_LH_BG4,
        bg5=_LH_BG5,
        bg_red=_LH_BG_RED,
        bg_yellow=_LH_BG_YELLOW,
        bg_green=_LH_BG_GREEN,
        bg_blue=_LH_BG_BLUE,
        bg_purple=_LH_BG_PURPLE,
        bg_visual=_LH_BG_VISUAL,
    ),
)

EVERFOREST_LIGHT_MEDIUM = Theme(
    name="everforest-light-medium",
    primary=_LIGHT_GREEN,
    secondary=_LIGHT_BLUE,
    accent=_LIGHT_PURPLE,
    warning=_LIGHT_YELLOW,
    error=_LIGHT_RED,
    success=_LIGHT_AQUA,
    foreground=_LIGHT_FG,
    background=_LM_BG0,
    surface=_LM_BG1,
    panel=_LM_BG2,
    dark=False,
    luminosity_spread=0.15,
    text_alpha=0.95,
    variables=_light_variables(
        bg_dim=_LM_BG_DIM,
        bg0=_LM_BG0,
        bg1=_LM_BG1,
        bg2=_LM_BG2,
        bg3=_LM_BG3,
        bg4=_LM_BG4,
        bg5=_LM_BG5,
        bg_red=_LM_BG_RED,
        bg_yellow=_LM_BG_YELLOW,
        bg_green=_LM_BG_GREEN,
        bg_blue=_LM_BG_BLUE,
        bg_purple=_LM_BG_PURPLE,
        bg_visual=_LM_BG_VISUAL,
    ),
)

EVERFOREST_LIGHT_SOFT = Theme(
    name="everforest-light-soft",
    primary=_LIGHT_GREEN,
    secondary=_LIGHT_BLUE,
    accent=_LIGHT_PURPLE,
    warning=_LIGHT_YELLOW,
    error=_LIGHT_RED,
    success=_LIGHT_AQUA,
    foreground=_LIGHT_FG,
    background=_LS_BG0,
    surface=_LS_BG1,
    panel=_LS_BG2,
    dark=False,
    luminosity_spread=0.15,
    text_alpha=0.95,
    variables=_light_variables(
        bg_dim=_LS_BG_DIM,
        bg0=_LS_BG0,
        bg1=_LS_BG1,
        bg2=_LS_BG2,
        bg3=_LS_BG3,
        bg4=_LS_BG4,
        bg5=_LS_BG5,
        bg_red=_LS_BG_RED,
        bg_yellow=_LS_BG_YELLOW,
        bg_green=_LS_BG_GREEN,
        bg_blue=_LS_BG_BLUE,
        bg_purple=_LS_BG_PURPLE,
        bg_visual=_LS_BG_VISUAL,
    ),
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

EVERFOREST_THEMES: list[Theme] = [
    EVERFOREST_DARK_HARD,
    EVERFOREST_DARK_MEDIUM,
    EVERFOREST_DARK_SOFT,
    EVERFOREST_LIGHT_HARD,
    EVERFOREST_LIGHT_MEDIUM,
    EVERFOREST_LIGHT_SOFT,
]
"""All six Everforest theme variants."""


def register_everforest_themes(app: App[Any]) -> None:
    """Register all Everforest theme variants with the given Textual app.

    After calling this, themes are available via the command palette and
    ``app.theme = "everforest-dark-hard"`` etc.
    """
    for theme in EVERFOREST_THEMES:
        app.register_theme(theme)
