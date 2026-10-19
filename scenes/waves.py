"""Wave superposition: constructive/destructive interference and standing waves."""

import numpy as np
from manim import *

from club_style import *

K = 2 * PI / 4.0  # wavenumber: wavelength of 4 units on the x axis
W = 2 * PI / 2.0  # angular frequency: period of 2 s
AMP = 0.7


class WaveInterference(ReelScene):
    def construct(self):
        self.intro("Wave Interference", "What happens when two waves meet?")

        def make_axes(y):
            return Axes(
                x_range=[0, 12, 1], y_range=[-1.6, 1.6, 1], x_length=7.6, y_length=2.0,
                axis_config={"color": MUTED, "include_tip": False, "stroke_width": 1.5},
                x_axis_config={"include_ticks": False}, y_axis_config={"include_ticks": False},
            ).move_to(UP * y)

        top, mid, bot = make_axes(3.7), make_axes(1.0), make_axes(-2.4)
        for ax in (top, mid, bot):
            ax.y_axis.set_opacity(0)
        names = [
            txt("Wave A", 26, CYAN, weight="BOLD").next_to(top, UP, 0.05).align_to(top, LEFT),
            txt("Wave B", 26, PINK, weight="BOLD").next_to(mid, UP, 0.05).align_to(mid, LEFT),
            txt("A + B", 30, ACCENT, weight="BOLD").next_to(bot, UP, 0.05).align_to(bot, LEFT),
        ]
        plus = txt("+", 44, MUTED).move_to((top.get_bottom() + mid.get_top()) / 2 + RIGHT * 3.6)
        equals = txt("=", 44, MUTED).move_to((mid.get_bottom() + bot.get_top()) / 2 + RIGHT * 3.6)

        t = ValueTracker(0)
        phase = ValueTracker(0)  # phase of B relative to A
        dir_b = ValueTracker(1)  # +1: B travels with A, -1: B travels the opposite way
        t.add_updater(lambda m, dt: m.increment_value(dt))

        def wave_a(x):
            return AMP * np.sin(K * x - W * t.get_value())

        def wave_b(x):
            return AMP * np.sin(K * x - dir_b.get_value() * W * t.get_value() + phase.get_value())

        ca = always_redraw(lambda: top.plot(wave_a, color=CYAN, stroke_width=5))
        cb = always_redraw(lambda: mid.plot(wave_b, color=PINK, stroke_width=5))
        cs = always_redraw(lambda: bot.plot(lambda x: wave_a(x) + wave_b(x), color=ACCENT, stroke_width=6))

        self.add(t)
        self.play(*[Create(a) for a in (top, mid, bot)], *[FadeIn(n) for n in names])
        self.play(Create(ca), Create(cb))
        self.play(FadeIn(plus), FadeIn(equals), Create(cs))

        phase_txt = live_text(
            lambda: f"phase difference: {np.degrees(phase.get_value()) % 360:.0f}°",
            lambda m: m.move_to(DOWN * 4.1), size=30, color=MUTED,
        )
        cap = self.caption("In step: the waves add up", y=-4.8, color=GREEN, weight="BOLD")
        self.play(FadeIn(phase_txt), FadeIn(cap))
        self.wait(3)

        new = self.caption("Out of step: they cancel out!", y=-4.8, color=PINK, weight="BOLD")
        self.play(phase.animate.set_value(PI), FadeTransform(cap, new), run_time=2.5)
        cap = new
        self.wait(3)
        new = self.caption("Anything in between: partial", y=-4.8, color=TEXT, weight="BOLD")
        self.play(phase.animate.set_value(2 * PI), FadeTransform(cap, new), run_time=4, rate_func=linear)
        cap = new
        self.wait(0.5)

        # ---- standing waves: B now travels the other way -----------------
        new = self.caption("Now send B the opposite way...", y=-4.8, color=ACCENT, weight="BOLD")
        arrows = VGroup(
            Arrow(LEFT * 0.6, RIGHT * 0.6, color=CYAN).next_to(names[0], RIGHT, 0.3),
            Arrow(RIGHT * 0.6, LEFT * 0.6, color=PINK).next_to(names[1], RIGHT, 0.3),
        )
        self.play(FadeOut(phase_txt), FadeTransform(cap, new), FadeIn(arrows))
        cap = new
        phase.set_value(0)
        dir_b.set_value(-1)
        self.wait(2.5)

        # Nodes of sin(kx - wt) + sin(kx + wt) = 2 sin(kx) cos(wt): where sin(kx) = 0.
        node_xs = [x for x in np.arange(0, 12.01, PI / K) if 0 < x < 12]
        nodes = VGroup(*[Dot(bot.c2p(x, 0), radius=0.1, color=GREEN) for x in node_xs])
        node_lbl = txt("nodes: never move", 28, GREEN).next_to(bot, DOWN, 0.2)
        new = self.caption("A standing wave!", y=-4.8, color=ACCENT, weight="BOLD")
        self.play(FadeIn(nodes, scale=2), FadeIn(node_lbl), FadeTransform(cap, new))
        cap = new
        self.wait(4)
        new = self.caption("Guitar strings vibrate like this", y=-4.8, color=TEXT)
        self.play(FadeTransform(cap, new))
        self.wait(2.5)

        t.clear_updaters()
        self.outro([
            "Overlapping waves simply add.",
            "In step → bigger wave.",
            "Out of step → they cancel.",
        ])
