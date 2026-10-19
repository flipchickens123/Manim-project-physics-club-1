"""Kepler's second law: a planet sweeps out equal areas in equal times."""

import numpy as np
from manim import *

from club_style import *

A = 3.6  # semi-major axis (scene units), drawn vertically
E = 0.6  # eccentricity
B = A * np.sqrt(1 - E ** 2)
PERIOD = 8.0  # seconds of screen time per orbit
CENTER = UP * 1.4
SWEEP = 0.9  # seconds of orbit swept for each area


def solve_kepler(M):
    """Eccentric anomaly E from mean anomaly M (Newton's method)."""
    Ea = M if E < 0.8 else PI
    for _ in range(30):
        Ea -= (Ea - E * np.sin(Ea) - M) / (1 - E * np.cos(Ea))
    return Ea


def orbit_point(t):
    """Position at time t (t=0 is perihelion). Major axis points down."""
    Ea = solve_kepler(2 * PI * t / PERIOD)
    along = A * np.cos(Ea)  # along major axis, from ellipse centre
    across = B * np.sin(Ea)
    return CENTER + np.array([across, -along, 0])


SUN = CENTER + np.array([0, -A * E, 0])


def sector_area(t0, t1, n=200):
    pts = np.array([SUN] + [orbit_point(t) for t in np.linspace(t0, t1, n)])
    x, y = pts[:, 0], pts[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def sector(t0, t1, color):
    pts = [SUN] + [orbit_point(t) for t in np.linspace(t0, t1, 60)]
    return Polygon(*pts, stroke_width=0, fill_color=color, fill_opacity=0.55)


class KeplerSecondLaw(ReelScene):
    def construct(self):
        self.intro("Kepler's 2nd Law", "Why planets speed up near the Sun")

        orbit = ParametricFunction(lambda s: orbit_point(s * PERIOD), t_range=[0, 1],
                                   color=MUTED, stroke_width=2)
        sun = VGroup(*[Dot(SUN, radius=r, color=ACCENT).set_opacity(o)
                       for r, o in ((0.5, 0.15), (0.38, 0.3), (0.26, 1))])
        np.random.seed(7)
        stars = VGroup(*[
            Dot([x, y, 0], radius=0.015 + 0.02 * np.random.rand(), color=TEXT).set_opacity(0.5)
            for x, y in zip(np.random.uniform(-4.3, 4.3, 60), np.random.uniform(-5, 6.5, 60))
        ])
        self.add(stars)
        self.bring_to_back(stars)
        self.play(FadeIn(sun, scale=0.5), Create(orbit), run_time=1.5)

        t = ValueTracker(0)
        planet = always_redraw(lambda: Dot(orbit_point(t.get_value()), radius=0.16, color=CYAN))

        def velocity():
            p, q = orbit_point(t.get_value()), orbit_point(t.get_value() + 0.01)
            v = (q - p) / 0.01 * 0.35
            return Arrow(p, p + v, buff=0, color=GREEN, stroke_width=5, max_tip_length_to_length_ratio=0.25)

        vel = always_redraw(velocity)
        speed = live_text(
            lambda: "speed: " + "▮" * int(round(np.linalg.norm(
                orbit_point(t.get_value() + 0.01) - orbit_point(t.get_value())) / 0.01 * 2)),
            lambda m: m.move_to(DOWN * 4.3).align_to(LEFT * 3.0, LEFT), size=30, color=GREEN,
        )
        cap = self.caption("Fast near the Sun, slow far away", y=-3.5, color=TEXT)
        self.play(FadeIn(planet), FadeIn(vel), FadeIn(speed), FadeIn(cap))
        self.play(t.animate.set_value(PERIOD), run_time=PERIOD, rate_func=linear)

        # ---- equal areas --------------------------------------------------
        new = self.caption(f"Shade {SWEEP} s of motion near the Sun...", y=-3.5, color=CYAN)
        self.play(FadeOut(speed), FadeTransform(cap, new))
        cap = new
        t.set_value(0)

        def sweep(t0, t1, color):
            t.set_value(t0)
            live = always_redraw(lambda: sector(t0, max(t.get_value(), t0 + 1e-3), color))
            self.add(live)
            self.bring_to_back(live)
            self.bring_to_back(stars)
            self.play(t.animate.set_value(t1), run_time=2.0, rate_func=linear)
            live.clear_updaters()
            return live

        s1 = sweep(PERIOD - SWEEP / 2, PERIOD + SWEEP / 2, CYAN)
        new = self.caption(f"...and {SWEEP} s far from the Sun", y=-3.5, color=PINK)
        self.play(FadeTransform(cap, new), t.animate.set_value(PERIOD * 1.5 - SWEEP / 2),
                  run_time=2, rate_func=linear)
        cap = new
        s2 = sweep(PERIOD * 1.5 - SWEEP / 2, PERIOD * 1.5 + SWEEP / 2, PINK)

        a1 = sector_area(-SWEEP / 2, SWEEP / 2)
        a2 = sector_area(PERIOD / 2 - SWEEP / 2, PERIOD / 2 + SWEEP / 2)
        result = panel(VGroup(
            txt("Same time → same area", 38, ACCENT, weight="BOLD"),
            VGroup(txt(f"area 1 = {a1:.2f}", 30, CYAN), txt(f"area 2 = {a2:.2f}", 30, PINK)
                   ).arrange(RIGHT, buff=0.6),
        ).arrange(DOWN, buff=0.3)).move_to(DOWN * 4.0)
        self.play(FadeOut(cap), FadeIn(result, shift=UP * 0.3))
        self.play(Indicate(s1, color=CYAN), Indicate(s2, color=PINK))
        self.play(t.animate.set_value(PERIOD * 2), run_time=2.5, rate_func=linear)
        self.wait(2)

        self.outro([
            "A planet sweeps equal areas",
            "in equal times, so it must",
            "move faster when it's close",
            "to the Sun.",
        ])
