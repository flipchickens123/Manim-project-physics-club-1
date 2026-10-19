"""Shared look and feel for the Physics Club Instagram animations.

Everything is drawn with ``Text`` (Pango), so no LaTeX install is needed.
Change CLUB_NAME / HANDLE below to rebrand every video at once.
"""

from contextlib import contextmanager

from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Circle,
    Dot,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    RoundedRectangle,
    Scene,
    Text,
    VGroup,
    Write,
    always_redraw,
)

CLUB_NAME = "PHYSICS CLUB"
HANDLE = "@hse.physics"
FONT = "Inter"  # falls back to the system sans-serif font if not installed

BG = "#0B1021"
PANEL = "#151B36"
TEXT = "#F1F3FF"
MUTED = "#8A93B8"
ACCENT = "#FFB000"  # yellow-orange
CYAN = "#4CC9F0"
PINK = "#F72585"
GREEN = "#7AE582"
PURPLE = "#B388FF"

# Frame is 9 x 16 units. Instagram's UI covers roughly the top ~1.8 and the
# bottom ~2.8 units of a Reel, so keep key content between these lines.
SAFE_TOP = 6.0
SAFE_BOTTOM = -5.2


def txt(s, size=36, color=TEXT, weight="NORMAL", **kw):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def live_text(fn, place, size=32, color=TEXT, **kw):
    """Text that re-renders every frame. ``fn`` returns the string and
    ``place`` receives the new Text mobject and positions it."""

    def build():
        t = txt(fn(), size=size, color=color, **kw)
        place(t)
        return t

    return always_redraw(build)


def panel(mobject, buff=0.35, color=PANEL, stroke=MUTED):
    box = RoundedRectangle(
        corner_radius=0.25,
        width=mobject.width + 2 * buff,
        height=mobject.height + 2 * buff,
        fill_color=color,
        fill_opacity=0.9,
        stroke_color=stroke,
        stroke_width=1.5,
    ).move_to(mobject)
    return VGroup(box, mobject)


def axis_labels(axes, xs=(), ys=(), size=22, fmt="{:g}"):
    """Tick labels made from Text (Axes' built-in numbers need LaTeX)."""
    group = VGroup()
    for x in xs:
        group.add(txt(fmt.format(x), size, MUTED).next_to(axes.c2p(x, axes.y_range[0]), DOWN, 0.15))
    for y in ys:
        group.add(txt(fmt.format(y), size, MUTED).next_to(axes.c2p(axes.x_range[0], y), LEFT, 0.15))
    return group


class ReelScene(Scene):
    """Base scene: branding bar, title card, closing card, optional narration."""

    # Set to a script name (scripts/<name>.md) to enable self.voiceover().
    narration_script = None
    narration_gap = 0.35  # seconds of quiet after each spoken section

    def setup(self):
        self.camera.background_color = BG
        if self.narration_script:
            import narration

            self._speak = narration.speak
            self.script = narration.load_script(self.narration_script)
        dot = Dot(radius=0.07, color=ACCENT)
        name = txt(CLUB_NAME, 26, ACCENT, weight="BOLD")
        self.brand = VGroup(dot, name).arrange(RIGHT, buff=0.15).move_to(UP * 6.9)
        self.handle = txt(HANDLE, 24, MUTED).move_to(DOWN * 6.9)

    @contextmanager
    def voiceover(self, section):
        """Speak one script section while the animations inside the block play.

        Yields the clip length (seconds) so animations can be timed to it. If the
        animations finish early, the scene waits for the voice to finish.
        """
        text = self.script[section]
        path, duration = self._speak(text)
        start = self.time
        self.add_sound(str(path))
        self.add_subcaption(text, duration=duration)
        yield duration
        left = start + duration + self.narration_gap - self.time
        if left > 0.05:
            self.wait(left)

    def intro(self, title, subtitle, hold=1.2):
        """Big title card, then shrinks the title into a header. Returns the header."""
        atom = self._atom().move_to(UP * 2.4)
        t = txt(title, 72, TEXT, weight="BOLD")
        if t.width > 8:
            t.scale_to_fit_width(8)
        s = txt(subtitle, 34, ACCENT)
        if s.width > 8:
            s.scale_to_fit_width(8)
        VGroup(t, s).arrange(DOWN, buff=0.4).move_to(DOWN * 0.3)

        self.play(FadeIn(self.brand, shift=DOWN * 0.3), FadeIn(self.handle, shift=UP * 0.3))
        self.play(FadeIn(atom, scale=0.5), Write(t), run_time=1.4)
        self.play(FadeIn(s, shift=UP * 0.2))
        self.wait(hold)

        header = txt(title, 46, TEXT, weight="BOLD").move_to(UP * 5.9)
        if header.width > 8.2:
            header.scale_to_fit_width(8.2)
        underline = Line(LEFT, RIGHT, color=ACCENT, stroke_width=4)
        underline.set_width(1.0).next_to(header, DOWN, 0.18)
        self.play(FadeOut(atom), FadeOut(s), t.animate.become(header), run_time=1)
        self.play(FadeIn(underline, scale=0.3), run_time=0.4)
        self.header = VGroup(t, underline)
        return self.header

    def caption(self, s, y=-4.6, size=34, color=TEXT, **kw):
        c = txt(s, size, color, **kw)
        if c.width > 8.2:
            c.scale_to_fit_width(8.2)
        return c.move_to(UP * y)

    def outro(self, lines, hold=2.5):
        """Clear the stage and show a takeaway card + follow prompt."""
        keep = {self.brand, self.handle}
        self.play(*[FadeOut(m) for m in self.mobjects if m not in keep], run_time=0.8)

        head = txt("KEY IDEA", 30, ACCENT, weight="BOLD")
        body = VGroup(*[txt(l, 38) for l in lines]).arrange(DOWN, buff=0.3)
        if body.width > 7.4:
            body.scale_to_fit_width(7.4)
        card = panel(VGroup(head, body).arrange(DOWN, buff=0.45), buff=0.5).move_to(UP * 1.2)
        follow = txt("Follow for more physics", 34, TEXT, weight="BOLD")
        handle = txt(HANDLE, 34, ACCENT)
        cta = VGroup(follow, handle).arrange(DOWN, buff=0.2).next_to(card, DOWN, buff=1.0)

        self.play(FadeIn(card[0], scale=0.9), FadeIn(head))
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in body], lag_ratio=0.35))
        self.play(FadeIn(cta, shift=UP * 0.3))
        if hold > 0:
            self.wait(hold)

    @staticmethod
    def _atom():
        nucleus = Dot(ORIGIN, radius=0.14, color=ACCENT)
        orbits = VGroup(
            *[
                Circle(radius=1, color=CYAN, stroke_width=3).stretch(0.35, 1).rotate(a)
                for a in (0, 1.047, 2.094)
            ]
        )
        return VGroup(orbits, nucleus)


__all__ = [
    "ACCENT", "BG", "CLUB_NAME", "CYAN", "FONT", "GREEN", "HANDLE", "MUTED",
    "PANEL", "PINK", "PURPLE", "ReelScene", "SAFE_BOTTOM", "SAFE_TOP", "TEXT",
    "axis_labels", "live_text", "panel", "txt",
]
