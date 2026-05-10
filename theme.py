"""Board colour themes."""

THEMES = {
    "Classic Wood": {
        "light_sq":  (240, 217, 181),
        "dark_sq":   (181, 136, 99),
        "bg":        (48, 46, 43),
        "panel_bg":  (38, 36, 33),
        "panel_txt": (210, 210, 210),
        "accent":    (130, 170, 100),
    },
    "Dark Slate": {
        "light_sq":  (175, 180, 190),
        "dark_sq":   (100, 110, 125),
        "bg":        (32, 33, 36),
        "panel_bg":  (26, 27, 30),
        "panel_txt": (195, 195, 200),
        "accent":    (90, 140, 220),
    },
    "Ice Blue": {
        "light_sq":  (215, 230, 245),
        "dark_sq":   (110, 145, 180),
        "bg":        (30, 40, 55),
        "panel_bg":  (22, 30, 42),
        "panel_txt": (200, 215, 230),
        "accent":    (70, 180, 220),
    },
}

THEME_NAMES = list(THEMES.keys())
_active_idx = 0


def active_theme():
    return THEMES[THEME_NAMES[_active_idx]]


def active_name():
    return THEME_NAMES[_active_idx]


def set_theme(name):
    global _active_idx
    if name in THEMES:
        _active_idx = THEME_NAMES.index(name)


def next_theme():
    global _active_idx
    _active_idx = (_active_idx + 1) % len(THEME_NAMES)
    return active_name()
