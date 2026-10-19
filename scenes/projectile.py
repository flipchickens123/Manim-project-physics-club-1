"""Projectile motion: independent x/y motion, then why 45 degrees goes farthest."""

import numpy as np
from manim import *

from club_style import *

G = 9.8
V0 = 20.0  # m/s


def position(t, angle_deg):
    a = np.radians(angle_deg)
    return V0 * np.cos(a) * t, V0 * np.sin(a) * t - 0.5 * G * t * t


def flight_time(angle_deg):
    return 2 * V0 * np.sin(np.radians(angle_deg)) / G


class ProjectileMotion(ReelScene):
    narration_script = "projectile"  # spoken lines live in scripts/projectile.md

    def construct(self):
        # Equal x/y scale (0.17 units per metre) so launch angles look right.
        axes = Axes(
            x_range=[0, 45, 10], y_range=[0, 20, 5], x_length=7.65, y_length=3.4,
            axis_config={"color": MUTED, "include_tip": False, "stroke_width": 2},
        ).move_to(UP * 2.7)
        ticks = axis_labels(axes, xs=(10, 20, 30, 40), ys=(5, 10, 15, 20))
        xl = txt("distance (m)", 22, MUTED).next_to(axes.x_axis, DOWN, 0.55)
        yl = txt("height (m)", 22, MUTED).next_to(axes.y_axis, UP, 0.15).align_to(axes, LEFT)

        with self.voiceover("intro"):
            self.intro("Projectile Motion", "Why does 45° go the farthest?", hold=0.6)
            self.play(Create(axes), FadeIn(ticks), FadeIn(xl), FadeIn(yl))

        # ---- Part 1: one launch, velocity split into components ----------
        angle = 50
        T = flight_time(angle)
        t = ValueTracker(0)
        a = np.radians(angle)
        k = 0.09  # arrow units per m/s

        ball = always_redraw(lambda: Dot(axes.c2p(*position(t.get_value(), angle)), radius=0.11, color=ACCENT))
        trail = TracedPath(ball.get_center, stroke_color=ACCENT, stroke_width=4)

        def components():
            p = ball.get_center()
            vx = V0 * np.cos(a)
            vy = V0 * np.sin(a) - G * t.get_value()
            g = VGroup(Arrow(p, p + RIGHT * vx * k, buff=0, color=CYAN, stroke_width=5,
                             max_tip_length_to_length_ratio=0.3))
            if abs(vy) > 0.6:
                g.add(Arrow(p, p + UP * vy * k, buff=0, color=PINK, stroke_width=5,
                            max_tip_length_to_length_ratio=0.3))
            return g

        arrows = always_redraw(components)

        def place_row(i):
            return lambda m: m.move_to(DOWN * (0.5 + 0.65 * i)).align_to(LEFT * 3.6, LEFT)

        readouts = VGroup(
            live_text(lambda: f"t = {t.get_value():.2f} s", place_row(0), color=TEXT),
            live_text(lambda: f"horizontal speed = {V0 * np.cos(a):.1f} m/s", place_row(1), color=CYAN),
            live_text(lambda: f"vertical speed = {V0 * np.sin(a) - G * t.get_value():+.1f} m/s",
                      place_row(2), color=PINK),
        )
        launch = self.caption(f"Launch: {V0:.0f} m/s at {angle}°", y=-2.9, color=ACCENT)

        with self.voiceover("launch"):
            self.add(trail)
            self.play(FadeIn(ball), FadeIn(arrows), FadeIn(readouts), FadeIn(launch))

        # The ball reaches the top as the narrator says "zero at the very top".
        with self.voiceover("rise") as d:
            self.play(t.animate.set_value(T / 2), run_time=d * 0.9, rate_func=linear)
        with self.voiceover("fall") as d:
            self.play(t.animate.set_value(T), run_time=d * 0.8, rate_func=linear)

        note = VGroup(
            txt("Horizontal: constant speed", 32, CYAN),
            txt("Vertical: gravity slows it, then speeds it up", 32, PINK),
        ).arrange(DOWN, buff=0.25).move_to(DOWN * 4.2)
        if note.width > 8.2:
            note.scale_to_fit_width(8.2)
        with self.voiceover("idea"):
            self.play(FadeIn(note[0], shift=UP * 0.2))
            self.play(FadeIn(note[1], shift=UP * 0.2))

        arrows.clear_updaters()
        readouts.clear_updaters()
        trail.clear_updaters()
        self.play(*[FadeOut(m) for m in (ball, arrows, readouts, launch, note, trail)], run_time=0.6)

        # ---- Part 2: same speed, five angles --------------------------------
        angles = [15, 30, 45, 60, 75]
        colors = [PURPLE, CYAN, ACCENT, PINK, GREEN]
        t2 = ValueTracker(0)

        def ball_at(ang):
            def f():
                tt = min(t2.get_value(), flight_time(ang))
                return Dot(axes.c2p(*position(tt, ang)), radius=0.09, color=colors[angles.index(ang)])
            return always_redraw(f)

        balls = [ball_at(ang) for ang in angles]
        trails = [TracedPath(b.get_center, stroke_color=b.get_color(), stroke_width=3.5) for b in balls]
        legend = VGroup(*[
            VGroup(Dot(color=c, radius=0.09), txt(f"{ang}°", 28, c)).arrange(RIGHT, buff=0.15)
            for ang, c in zip(angles, colors)
        ]).arrange(RIGHT, buff=0.45).move_to(DOWN * 0.7)
        q = self.caption("Same speed. Which angle lands farthest?", y=-1.9, size=32)

        with self.voiceover("angles") as d:
            self.add(*trails)
            self.play(LaggedStart(*[FadeIn(m) for m in legend], lag_ratio=0.5),
                      *[FadeIn(b) for b in balls], run_time=d * 0.55)
            self.play(FadeIn(q), run_time=0.5)
            self.play(t2.animate.set_value(flight_time(75)), run_time=max(4.0, d * 0.45), rate_func=linear)
        for b in balls + trails:
            b.clear_updaters()

        best = axes.c2p(V0 ** 2 / G, 0)
        ring = Circle(radius=0.22, color=ACCENT, stroke_width=5).move_to(best)
        win = self.caption(f"45° lands farthest: {V0 ** 2 / G:.1f} m", y=-1.9, size=34,
                           color=ACCENT, weight="BOLD")
        same = position(flight_time(30), 30)[0]
        pair = DashedLine(axes.c2p(same, 0) + UP * 0.05, axes.c2p(same, 9.5), color=MUTED)
        pair_text = txt("30° and 60° tie!", 26, TEXT).next_to(pair, UP, 0.1)
        with self.voiceover("winner") as d:
            self.play(FadeOut(q), Create(ring), trails[2].animate.set_stroke(width=7), FadeIn(win))
            self.wait(d * 0.4)
            self.play(Create(pair), FadeIn(pair_text))

        formula = VGroup(
            txt("range = v² · sin(2θ) / g", 38, TEXT),
            txt("sin(2θ) is largest when 2θ = 90°", 28, MUTED),
        ).arrange(DOWN, buff=0.25)
        box = panel(formula).move_to(DOWN * 3.8)
        with self.voiceover("formula") as d:
            self.play(FadeIn(box[0]), FadeIn(formula[0], shift=UP * 0.2))
            self.wait(d * 0.45)
            self.play(FadeIn(formula[1], shift=UP * 0.2))

        with self.voiceover("outro"):
            self.outro([
                "x and y motion are independent.",
                "With no air resistance,",
                "45° gives the longest range.",
            ], hold=0)
        self.wait(1.5)
