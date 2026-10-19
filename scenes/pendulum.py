"""Simple pendulum: energy sloshing between kinetic and potential."""

import numpy as np
from manim import *

from club_style import *

G = 9.8
L = 2.0  # metres
THETA0 = np.radians(60)
DURATION = 9.0  # seconds of simulated (and on-screen) time
CAP_Y = 1.0  # caption line between the pendulum and the energy bars


def simulate(dt=1 / 600):
    """RK4 for theta'' = -(g/L) sin(theta). Returns (times, theta, omega)."""
    def f(state):
        th, om = state
        return np.array([om, -(G / L) * np.sin(th)])

    n = int(DURATION / dt) + 1
    out = np.zeros((n, 2))
    s = np.array([THETA0, 0.0])
    for i in range(n):
        out[i] = s
        k1 = f(s)
        k2 = f(s + dt / 2 * k1)
        k3 = f(s + dt / 2 * k2)
        k4 = f(s + dt * k3)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return np.arange(n) * dt, out[:, 0], out[:, 1]


class Pendulum(ReelScene):
    def construct(self):
        self.intro("The Pendulum", "Energy never disappears, it just changes form")

        times, thetas, omegas = simulate()
        t = ValueTracker(0)

        def theta():
            return np.interp(t.get_value(), times, thetas)

        def omega():
            return np.interp(t.get_value(), times, omegas)

        # ---- pendulum -----------------------------------------------------
        pivot = UP * 5.0
        rod_len = 2.8  # scene units
        ceiling = Line(pivot + LEFT * 1.2, pivot + RIGHT * 1.2, color=MUTED, stroke_width=4)
        hatch = VGroup(*[
            Line(pivot + RIGHT * x, pivot + RIGHT * (x + 0.2) + UP * 0.2, color=MUTED, stroke_width=2)
            for x in np.arange(-1.1, 1.2, 0.25)
        ])

        def bob_pos():
            th = theta()
            return pivot + rod_len * np.array([np.sin(th), -np.cos(th), 0])

        rod = always_redraw(lambda: Line(pivot, bob_pos(), color=TEXT, stroke_width=4))
        bob = always_redraw(lambda: Dot(bob_pos(), radius=0.25, color=ACCENT))
        rest = DashedLine(pivot, pivot + DOWN * rod_len, color=MUTED, stroke_width=2)
        swing = Arc(radius=rod_len, start_angle=-PI / 2 - THETA0, angle=2 * THETA0,
                    arc_center=pivot, color=MUTED, stroke_width=2).set_stroke(opacity=0.5)

        self.play(Create(ceiling), FadeIn(hatch), Create(rest), Create(swing))
        self.play(Create(rod), FadeIn(bob, scale=0.5))

        # ---- energy bars --------------------------------------------------
        e_total = G * L * (1 - np.cos(THETA0))  # per unit mass

        def pe():
            return G * L * (1 - np.cos(theta())) / e_total

        def ke():
            return 0.5 * (L * omega()) ** 2 / e_total

        bar_h, bar_w = 2.2, 1.1
        base_y = -1.9
        xs = {"KE": -2.4, "PE": 0.0, "Total": 2.4}
        cols = {"KE": CYAN, "PE": PINK, "Total": GREEN}
        fns = {"KE": ke, "PE": pe, "Total": lambda: ke() + pe()}

        frames = VGroup()
        labels = VGroup()
        bars = VGroup()
        for name, x in xs.items():
            frame = Rectangle(width=bar_w, height=bar_h, color=MUTED, stroke_width=2)
            frame.move_to([x, base_y + bar_h / 2, 0])
            frames.add(frame)
            labels.add(txt(name, 28, cols[name], weight="BOLD").next_to(frame, DOWN, 0.2))

            def make(name=name, x=x):
                h = max(min(fns[name](), 1.0), 0.0) * bar_h
                r = Rectangle(width=bar_w, height=max(h, 0.001), stroke_width=0,
                              fill_color=cols[name], fill_opacity=0.85)
                return r.move_to([x, base_y + h / 2, 0])

            bars.add(always_redraw(make))

        plus = txt("+", 40, MUTED).move_to([(xs["KE"] + xs["PE"]) / 2, base_y + bar_h / 2, 0])
        eq = txt("=", 40, MUTED).move_to([(xs["PE"] + xs["Total"]) / 2, base_y + bar_h / 2, 0])
        self.play(Create(frames), FadeIn(labels), FadeIn(bars), FadeIn(plus), FadeIn(eq))

        # ---- angle vs time graph -----------------------------------------
        axes = Axes(
            x_range=[0, DURATION, 1], y_range=[-60, 60, 30], x_length=7.4, y_length=1.9,
            axis_config={"color": MUTED, "include_tip": False, "stroke_width": 2},
        ).move_to(DOWN * 4.0)
        gl = txt("angle", 22, MUTED).next_to(axes.y_axis, UP, 0.1).align_to(axes, LEFT)
        tl = txt("time", 22, MUTED).next_to(axes.x_axis.get_right(), DOWN, 0.15)
        ticks = axis_labels(axes, ys=(-60, 60), fmt="{:+g}°", size=18)
        pen = always_redraw(lambda: Dot(axes.c2p(t.get_value(), np.degrees(theta())), radius=0.05, color=ACCENT))
        curve = TracedPath(pen.get_center, stroke_color=ACCENT, stroke_width=3)
        self.play(Create(axes), FadeIn(gl), FadeIn(tl), FadeIn(ticks))
        self.add(curve, pen)

        # ---- swing! -------------------------------------------------------
        cap = self.caption("Top: all potential energy", y=CAP_Y, size=30, color=PINK)
        self.play(FadeIn(cap))
        # Period = time of first return to rest on the starting side.
        period = times[np.where((omegas[:-1] > 0) & (omegas[1:] <= 0))[0][0] + 1]
        notes = [
            (0.25 * period, "Bottom: all kinetic energy", CYAN),
            (0.50 * period, "Other side: back to potential", PINK),
            (1.00 * period, "The total stays the same", GREEN),
        ]
        last = 0.0
        for when, msg, col in notes:
            self.play(t.animate.set_value(when), run_time=when - last, rate_func=linear)
            last = when
            new = self.caption(msg, y=CAP_Y, size=30, color=col)
            self.remove(cap)
            self.add(new)
            cap = new
        self.play(t.animate.set_value(DURATION), run_time=DURATION - last, rate_func=linear)

        for m in (rod, bob, pen, curve, *bars):
            m.clear_updaters()
        fact = panel(VGroup(
            txt(f"One full swing: {period:.2f} s", 34, TEXT),
            txt("Small-angle estimate  2π√(L/g):  " + f"{2 * np.pi * np.sqrt(L / G):.2f} s", 24, MUTED),
        ).arrange(DOWN, buff=0.2)).move_to(UP * CAP_Y)
        self.play(FadeOut(cap), FadeIn(fact, shift=UP * 0.2))
        self.wait(3)

        self.outro([
            "Potential energy turns into",
            "kinetic energy and back again.",
            "Without friction, the total",
            "never changes.",
        ])
